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
            "requested_quantity": 12,
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
            "requested_quantity": 12,
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
