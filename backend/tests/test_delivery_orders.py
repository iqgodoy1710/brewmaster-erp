def create_delivery_order_context(client):
    customer_response = client.post(
        "/customers/",
        json={
            "name": "Delivery Order Customer",
        },
    )
    assert customer_response.status_code == 201

    beer_response = client.post(
        "/beers/",
        json={
            "name": "Delivery Order Beer",
            "style": "Blonde Ale",
        },
    )
    assert beer_response.status_code == 201

    format_response = client.post(
        "/packaging-formats/",
        json={
            "name": "Delivery Order Bottle 500 ml",
            "capacity_liters": "0.500",
            "format_type": "bottle",
        },
    )
    assert format_response.status_code == 201

    presentation_response = client.post(
        "/beer-presentations/",
        json={
            "name": "Delivery Order Beer Bottle 500 ml",
            "beer_id": beer_response.json()["id"],
            "packaging_format_id": format_response.json()["id"],
        },
    )
    assert presentation_response.status_code == 201

    presentation = presentation_response.json()

    stock_response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": presentation["id"],
            "movement_type": "initial_balance",
            "quantity": 20,
        },
    )
    assert stock_response.status_code == 201

    return {
        "customer": customer_response.json(),
        "presentation": presentation,
    }


def test_create_delivery_order_and_pick_items(client):
    context = create_delivery_order_context(client)

    order_response = client.post(
        "/delivery-orders/",
        json={
            "customer_id": context["customer"]["id"],
            "notes": "Weekly delivery.",
        },
    )
    assert order_response.status_code == 201

    order = order_response.json()

    assert order["code"] == "PED-000001"
    assert order["status"] == "draft"
    assert order["delivery_note_code"] is None

    item_response = client.post(
        f"/delivery-orders/{order['code']}/items",
        json={
            "beer_presentation_id": context["presentation"]["id"],
            "requested_quantity": 12,
        },
    )
    assert item_response.status_code == 201

    item = item_response.json()

    picking_start_response = client.post(
        f"/delivery-orders/{order['code']}/start-picking",
    )
    assert picking_start_response.status_code == 200
    assert picking_start_response.json()["status"] == "picking"

    picking_response = client.patch(
        f"/delivery-orders/{order['code']}/items/{item['id']}/picking",
        json={
            "picked_quantity": 10,
        },
    )
    assert picking_response.status_code == 200
    assert picking_response.json()["picked_quantity"] == 10

    detail_response = client.get(
        f"/delivery-orders/{order['code']}",
    )
    assert detail_response.status_code == 200

    detail = detail_response.json()

    assert detail["status"] == "picking"
    assert len(detail["items"]) == 1
    assert detail["items"][0]["requested_quantity"] == 12
    assert detail["items"][0]["picked_quantity"] == 10
    assert detail["items"][0]["delivered_quantity"] == 0


def test_delivering_bottles_updates_stock_and_creates_delivery_traceability(
    client,
):
    context = create_delivery_order_context(client)

    order_response = client.post(
        "/delivery-orders/",
        json={
            "customer_id": context["customer"]["id"],
        },
    )
    assert order_response.status_code == 201

    order = order_response.json()

    item_response = client.post(
        f"/delivery-orders/{order['code']}/items",
        json={
            "beer_presentation_id": context["presentation"]["id"],
            "requested_quantity": 10,
        },
    )
    assert item_response.status_code == 201

    item = item_response.json()

    assert (
        client.post(
            f"/delivery-orders/{order['code']}/start-picking",
        ).status_code
        == 200
    )

    assert (
        client.patch(
            f"/delivery-orders/{order['code']}/items/{item['id']}/picking",
            json={"picked_quantity": 10},
        ).status_code
        == 200
    )

    delivery_response = client.post(
        f"/delivery-orders/{order['code']}/deliver",
        json={
            "notes": "Delivered with the route truck.",
        },
    )
    assert delivery_response.status_code == 200

    delivered_order = delivery_response.json()

    assert delivered_order["status"] == "delivered_pending_pricing"
    assert delivered_order["delivery_note_code"] == "REM-000001"

    presentations = client.get("/beer-presentations/").json()
    presentation = next(
        presentation
        for presentation in presentations
        if presentation["id"] == context["presentation"]["id"]
    )

    assert presentation["current_stock"] == 10

    movements = client.get(
        f"/beer-presentations/{context['presentation']['id']}/stock-movements"
    ).json()

    assert movements[0]["movement_type"] == "delivery"
    assert movements[0]["quantity"] == 10
    assert movements[0]["delivery_order_id"] == order["id"]
    assert movements[0]["reference"] == delivered_order["delivery_note_code"]

    detail = client.get(
        f"/delivery-orders/{order['code']}",
    ).json()

    assert detail["items"][0]["delivered_quantity"] == 10


def test_closing_delivered_order_creates_sale_and_account_charge(
    client,
):
    context = create_delivery_order_context(client)

    order = client.post(
        "/delivery-orders/",
        json={
            "customer_id": context["customer"]["id"],
        },
    ).json()

    item = client.post(
        f"/delivery-orders/{order['code']}/items",
        json={
            "beer_presentation_id": context["presentation"]["id"],
            "requested_quantity": 10,
        },
    ).json()

    assert (
        client.post(
            f"/delivery-orders/{order['code']}/start-picking",
        ).status_code
        == 200
    )

    assert (
        client.patch(
            f"/delivery-orders/{order['code']}/items/{item['id']}/picking",
            json={"picked_quantity": 10},
        ).status_code
        == 200
    )

    assert (
        client.post(
            f"/delivery-orders/{order['code']}/deliver",
            json={},
        ).status_code
        == 200
    )

    close_response = client.post(
        f"/delivery-orders/{order['code']}/close",
        json={
            "items": [
                {
                    "delivery_order_item_id": item["id"],
                    "unit_price": "12.50",
                }
            ],
        },
    )

    assert close_response.status_code == 200

    sale = close_response.json()
    assert sale["code"] == "VEN-000001"
    assert sale["status"] == "completed"

    presentation = next(
        presentation
        for presentation in client.get("/beer-presentations/").json()
        if presentation["id"] == context["presentation"]["id"]
    )
    assert presentation["current_stock"] == 10

    order_detail = client.get(
        f"/delivery-orders/{order['code']}",
    ).json()
    assert order_detail["status"] == "closed"

    account = client.get(
        f"/customers/{context['customer']['id']}/account",
    ).json()
    assert account["balance"] == "125.00"
    assert account["movements"][0]["movement_type"] == "sale_charge"
    assert account["movements"][0]["sale_code"] == sale["code"]


def test_delivery_order_items_can_be_safely_edited_during_picking(
    client,
):
    context = create_delivery_order_context(client)

    order = client.post(
        "/delivery-orders/",
        json={
            "customer_id": context["customer"]["id"],
        },
    ).json()

    original_item_response = client.post(
        f"/delivery-orders/{order['code']}/items",
        json={
            "beer_presentation_id": context["presentation"]["id"],
            "requested_quantity": 10,
        },
    )
    assert original_item_response.status_code == 201

    original_item = original_item_response.json()

    start_response = client.post(
        f"/delivery-orders/{order['code']}/start-picking",
    )
    assert start_response.status_code == 200

    picking_response = client.patch(
        (f"/delivery-orders/{order['code']}/items/{original_item['id']}/picking"),
        json={
            "picked_quantity": 4,
        },
    )
    assert picking_response.status_code == 200

    invalid_update_response = client.patch(
        (f"/delivery-orders/{order['code']}/items/{original_item['id']}"),
        json={
            "requested_quantity": 3,
        },
    )
    assert invalid_update_response.status_code == 409
    assert invalid_update_response.json() == {
        "detail": ("The requested quantity cannot be lower than the picked quantity.")
    }

    valid_update_response = client.patch(
        (f"/delivery-orders/{order['code']}/items/{original_item['id']}"),
        json={
            "requested_quantity": 6,
        },
    )
    assert valid_update_response.status_code == 200
    assert valid_update_response.json()["requested_quantity"] == 6

    second_format_response = client.post(
        "/packaging-formats/",
        json={
            "name": "Delivery Order Bottle 330 ml",
            "capacity_liters": "0.330",
            "format_type": "bottle",
        },
    )
    assert second_format_response.status_code == 201

    second_presentation_response = client.post(
        "/beer-presentations/",
        json={
            "name": "Delivery Order Beer Bottle 330 ml",
            "beer_id": context["presentation"]["beer_id"],
            "packaging_format_id": (second_format_response.json()["id"]),
        },
    )
    assert second_presentation_response.status_code == 201

    added_item_response = client.post(
        f"/delivery-orders/{order['code']}/items",
        json={
            "beer_presentation_id": (second_presentation_response.json()["id"]),
            "requested_quantity": 5,
        },
    )
    assert added_item_response.status_code == 201
    assert added_item_response.json()["picked_quantity"] == 0

    added_item = added_item_response.json()

    remove_unpicked_response = client.delete(
        (f"/delivery-orders/{order['code']}/items/{added_item['id']}"),
    )
    assert remove_unpicked_response.status_code == 204

    remove_picked_response = client.delete(
        (f"/delivery-orders/{order['code']}/items/{original_item['id']}"),
    )
    assert remove_picked_response.status_code == 409
    assert remove_picked_response.json() == {
        "detail": "A picked delivery order item cannot be removed."
    }

    detail_response = client.get(
        f"/delivery-orders/{order['code']}",
    )
    assert detail_response.status_code == 200

    detail = detail_response.json()

    assert len(detail["items"]) == 1
    assert detail["items"][0]["id"] == original_item["id"]
    assert detail["items"][0]["requested_quantity"] == 6
    assert detail["items"][0]["picked_quantity"] == 4


def test_closing_delivery_order_item_saves_quantity_and_completes_it(
    client,
):
    context = create_delivery_order_context(client)

    order = client.post(
        "/delivery-orders/",
        json={
            "customer_id": context["customer"]["id"],
        },
    ).json()

    item_response = client.post(
        f"/delivery-orders/{order['code']}/items",
        json={
            "beer_presentation_id": context["presentation"]["id"],
            "requested_quantity": 10,
        },
    )
    assert item_response.status_code == 201

    item = item_response.json()

    start_response = client.post(
        f"/delivery-orders/{order['code']}/start-picking",
    )
    assert start_response.status_code == 200

    close_response = client.post(
        (
            f"/delivery-orders/{order['code']}"
            f"/items/{item['id']}/close"
        ),
        json={
            "requested_quantity": 7,
        },
    )

    assert close_response.status_code == 200

    closed_item = close_response.json()

    assert closed_item["requested_quantity"] == 7
    assert closed_item["picked_quantity"] == 7

    detail_response = client.get(
        f"/delivery-orders/{order['code']}",
    )
    assert detail_response.status_code == 200

    detail_item = detail_response.json()["items"][0]

    assert detail_item["requested_quantity"] == 7
    assert detail_item["picked_quantity"] == 7

def test_cannot_deliver_order_with_open_items(client):
    context = create_delivery_order_context(client)

    order = client.post(
        "/delivery-orders/",
        json={
            "customer_id": context["customer"]["id"],
        },
    ).json()

    item = client.post(
        f"/delivery-orders/{order['code']}/items",
        json={
            "beer_presentation_id": context["presentation"]["id"],
            "requested_quantity": 10,
        },
    ).json()

    start_response = client.post(
        f"/delivery-orders/{order['code']}/start-picking",
    )
    assert start_response.status_code == 200

    picking_response = client.patch(
        (
            f"/delivery-orders/{order['code']}"
            f"/items/{item['id']}/picking"
        ),
        json={
            "picked_quantity": 5,
        },
    )
    assert picking_response.status_code == 200

    delivery_response = client.post(
        f"/delivery-orders/{order['code']}/deliver",
        json={},
    )

    assert delivery_response.status_code == 409
    assert delivery_response.json() == {
        "detail": (
            "All delivery order items must be closed "
            "before delivery."
        )
    }