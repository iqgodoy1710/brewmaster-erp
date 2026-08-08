def create_test_customer(client):
    response = client.post(
        "/customers/",
        json={
            "code": "CLI-SALE-TEST",
            "name": "Sale Test Customer",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_sale_as_draft(client):
    customer = create_test_customer(client)

    creation_response = client.post(
        "/sales/",
        json={
            "code": "SALE-TEST-001",
            "customer_id": customer["id"],
            "notes": "Test sale.",
        },
    )

    assert creation_response.status_code == 201

    sale = creation_response.json()

    assert sale["customer_id"] == customer["id"]
    assert sale["status"] == "draft"
    assert sale["completed_at"] is None

    list_response = client.get("/sales/")

    assert list_response.status_code == 200
    assert list_response.json() == [sale]


def create_test_beer_presentation(client):
    beer_response = client.post(
        "/beers/",
        json={
            "code": "IPA-SALE-TEST",
            "name": "IPA Sale Test",
        },
    )
    assert beer_response.status_code == 201

    beer = beer_response.json()

    packaging_format_response = client.post(
        "/packaging-formats/",
        json={
            "code": "BOTTLE-SALE-TEST",
            "name": "Bottle Sale Test",
            "capacity_liters": "0.500",
        },
    )
    assert packaging_format_response.status_code == 201

    packaging_format = packaging_format_response.json()

    beer_presentation_response = client.post(
        "/beer-presentations/",
        json={
            "code": "IPA-B500-SALE-TEST",
            "name": "IPA Bottle 500 ml Sale Test",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
        },
    )
    assert beer_presentation_response.status_code == 201

    return beer_presentation_response.json()


def test_create_and_get_sale_items(client):
    customer = create_test_customer(client)
    beer_presentation = create_test_beer_presentation(client)

    sale = client.post(
        "/sales/",
        json={
            "code": "SALE-TEST-001",
            "customer_id": customer["id"],
        },
    ).json()

    creation_response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["id"],
            "beer_presentation_id": beer_presentation["id"],
            "quantity": 5,
            "unit_price": "4.50",
        },
    )

    assert creation_response.status_code == 201

    sale_item = creation_response.json()

    assert sale_item["sale_id"] == sale["id"]
    assert sale_item["beer_presentation_id"] == beer_presentation["id"]

    list_response = client.get(f"/sales/{sale['id']}/items")

    assert list_response.status_code == 200
    assert list_response.json() == [sale_item]

def test_complete_sale_consumes_finished_product_stock(client):
    customer = create_test_customer(client)
    beer_presentation = create_test_beer_presentation(client)

    initial_stock_response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "movement_type": "initial_balance",
            "quantity": 10,
            "reference": "INITIAL-SALE-TEST",
        },
    )
    assert initial_stock_response.status_code == 201

    sale = client.post(
        "/sales/",
        json={
            "code": "SALE-TEST-001",
            "customer_id": customer["id"],
        },
    ).json()

    sale_item_response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["id"],
            "beer_presentation_id": beer_presentation["id"],
            "quantity": 5,
            "unit_price": "4.50",
        },
    )
    assert sale_item_response.status_code == 201

    completion_response = client.post(
        f"/sales/{sale['code']}/complete"
    )

    assert completion_response.status_code == 200

    completed_sale = completion_response.json()

    assert completed_sale["status"] == "completed"
    assert completed_sale["completed_at"] is not None

    beer_presentations = client.get("/beer-presentations/").json()
    updated_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == beer_presentation["id"]
    )
    assert updated_presentation["current_stock"] == 5

    movements = client.get(
        f"/beer-presentations/{beer_presentation['id']}/stock-movements"
    ).json()

    assert movements[0]["movement_type"] == "sale"
    assert movements[0]["sale_id"] == sale["id"]
    assert movements[0]["quantity"] == 5
    assert movements[0]["reference"] == sale["code"]

def test_cannot_complete_sale_without_items(client):
    customer = create_test_customer(client)

    sale = client.post(
        "/sales/",
        json={
            "code": "SALE-TEST-NO-ITEMS",
            "customer_id": customer["id"],
        },
    ).json()

    response = client.post(
        f"/sales/{sale['code']}/complete"
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Cannot complete a sale without items."
    }

    sales = client.get("/sales/").json()

    assert sales[0]["status"] == "draft"
    assert sales[0]["completed_at"] is None

def test_complete_sale_with_insufficient_stock_is_atomic(client):
    customer = create_test_customer(client)
    beer_presentation = create_test_beer_presentation(client)

    initial_stock_response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "movement_type": "initial_balance",
            "quantity": 5,
            "reference": "INITIAL-INSUFFICIENT-SALE-TEST",
        },
    )
    assert initial_stock_response.status_code == 201

    sale = client.post(
        "/sales/",
        json={
            "code": "SALE-TEST-INSUFFICIENT",
            "customer_id": customer["id"],
        },
    ).json()

    sale_item_response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["id"],
            "beer_presentation_id": beer_presentation["id"],
            "quantity": 10,
            "unit_price": "4.50",
        },
    )
    assert sale_item_response.status_code == 201

    response = client.post(f"/sales/{sale['code']}/complete")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "There is not enough stock for a beer presentation."
    }

    beer_presentations = client.get("/beer-presentations/").json()
    updated_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == beer_presentation["id"]
    )
    assert updated_presentation["current_stock"] == 5

    movements = client.get(
        f"/beer-presentations/{beer_presentation['id']}/stock-movements"
    ).json()
    assert len(movements) == 1
    assert movements[0]["movement_type"] == "initial_balance"

    sales = client.get("/sales/").json()
    assert sales[0]["status"] == "draft"
    assert sales[0]["completed_at"] is None

def test_completed_sale_cannot_be_completed_again(client):
    customer = create_test_customer(client)
    beer_presentation = create_test_beer_presentation(client)

    initial_stock_response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "movement_type": "initial_balance",
            "quantity": 10,
            "reference": "INITIAL-DOUBLE-COMPLETE-TEST",
        },
    )
    assert initial_stock_response.status_code == 201

    sale = client.post(
        "/sales/",
        json={
            "code": "SALE-TEST-DOUBLE-COMPLETE",
            "customer_id": customer["id"],
        },
    ).json()

    sale_item_response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["id"],
            "beer_presentation_id": beer_presentation["id"],
            "quantity": 5,
            "unit_price": "4.50",
        },
    )
    assert sale_item_response.status_code == 201

    first_completion_response = client.post(
        f"/sales/{sale['code']}/complete"
    )
    assert first_completion_response.status_code == 200

    second_completion_response = client.post(
        f"/sales/{sale['code']}/complete"
    )

    assert second_completion_response.status_code == 409
    assert second_completion_response.json() == {
        "detail": "Only draft sales can be completed."
    }

    beer_presentations = client.get("/beer-presentations/").json()
    updated_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == beer_presentation["id"]
    )
    assert updated_presentation["current_stock"] == 5

def test_cancel_completed_sale_returns_finished_product_stock(client):
    customer = create_test_customer(client)
    beer_presentation = create_test_beer_presentation(client)

    initial_stock_response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "movement_type": "initial_balance",
            "quantity": 10,
            "reference": "INITIAL-CANCEL-SALE-TEST",
        },
    )
    assert initial_stock_response.status_code == 201

    sale = client.post(
        "/sales/",
        json={
            "code": "SALE-TEST-CANCEL",
            "customer_id": customer["id"],
        },
    ).json()

    sale_item_response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["id"],
            "beer_presentation_id": beer_presentation["id"],
            "quantity": 5,
            "unit_price": "4.50",
        },
    )
    assert sale_item_response.status_code == 201

    completion_response = client.post(
        f"/sales/{sale['code']}/complete"
    )
    assert completion_response.status_code == 200

    cancellation_response = client.post(
        f"/sales/{sale['code']}/cancel",
        json={
            "cancellation_reason": "Customer cancelled the order.",
        },
    )

    assert cancellation_response.status_code == 200

    cancelled_sale = cancellation_response.json()

    assert cancelled_sale["status"] == "cancelled"
    assert cancelled_sale["completed_at"] is not None
    assert cancelled_sale["cancelled_at"] is not None
    assert (
        cancelled_sale["cancellation_reason"]
        == "Customer cancelled the order."
    )

    beer_presentations = client.get("/beer-presentations/").json()
    updated_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == beer_presentation["id"]
    )
    assert updated_presentation["current_stock"] == 10

    movements = client.get(
        f"/beer-presentations/{beer_presentation['id']}/stock-movements"
    ).json()

    assert movements[0]["movement_type"] == "inventory_adjustment_in"
    assert movements[0]["sale_id"] == sale["id"]
    assert movements[0]["quantity"] == 5
    assert movements[0]["reference"] == sale["code"]

def test_cancel_draft_sale_does_not_change_stock(client):
    customer = create_test_customer(client)

    sale = client.post(
        "/sales/",
        json={
            "code": "SALE-TEST-CANCEL-DRAFT",
            "customer_id": customer["id"],
        },
    ).json()

    cancellation_response = client.post(
        f"/sales/{sale['code']}/cancel",
        json={
            "cancellation_reason": "Draft no longer needed.",
        },
    )

    assert cancellation_response.status_code == 200

    cancelled_sale = cancellation_response.json()

    assert cancelled_sale["status"] == "cancelled"
    assert cancelled_sale["completed_at"] is None
    assert cancelled_sale["cancelled_at"] is not None
    assert (
        cancelled_sale["cancellation_reason"]
        == "Draft no longer needed."
    )

def test_cancelled_sale_cannot_be_cancelled_again(client):
    customer = create_test_customer(client)

    sale = client.post(
        "/sales/",
        json={
            "code": "SALE-TEST-DOUBLE-CANCEL",
            "customer_id": customer["id"],
        },
    ).json()

    first_cancellation_response = client.post(
        f"/sales/{sale['code']}/cancel",
        json={
            "cancellation_reason": "First cancellation.",
        },
    )
    assert first_cancellation_response.status_code == 200

    second_cancellation_response = client.post(
        f"/sales/{sale['code']}/cancel",
        json={
            "cancellation_reason": "Second cancellation.",
        },
    )

    assert second_cancellation_response.status_code == 409
    assert second_cancellation_response.json() == {
        "detail": "Only draft or completed sales can be cancelled."
    }

def test_get_sale_detail_includes_customer_items_and_total(client):
    beer_presentation = create_test_beer_presentation(client)

    customer_response = client.post(
        "/customers/",
        json={
            "code": "CUSTOMER-DETAIL",
            "name": "Detail Customer",
        },
    )
    assert customer_response.status_code == 201

    customer = customer_response.json()

    sale_response = client.post(
        "/sales/",
        json={
            "code": "SALE-DETAIL-001",
            "customer_id": customer["id"],
            "notes": "Sale detail report test.",
        },
    )
    assert sale_response.status_code == 201

    sale = sale_response.json()

    item_response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["id"],
            "beer_presentation_id": beer_presentation["id"],
            "quantity": 3,
            "unit_price": "4.50",
        },
    )
    assert item_response.status_code == 201

    response = client.get("/sales/SALE-DETAIL-001/detail")

    assert response.status_code == 200

    detail = response.json()

    assert detail["code"] == "SALE-DETAIL-001"
    assert detail["customer_id"] == customer["id"]
    assert detail["customer_name"] == "Detail Customer"
    assert detail["status"] == "draft"
    assert detail["total_amount"] == "13.50"
    assert detail["items"] == [
        {
            "beer_presentation_id": beer_presentation["id"],
            "beer_presentation_code": beer_presentation["code"],
            "beer_presentation_name": beer_presentation["name"],
            "quantity": 3,
            "unit_price": "4.50",
            "line_total": "13.50",
        }
    ]