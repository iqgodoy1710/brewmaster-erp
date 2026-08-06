def create_test_beer_presentation(client):
    beer_response = client.post(
        "/beers/",
        json={
            "code": "IPA-STOCK-TEST",
            "name": "IPA Stock Test",
        },
    )
    assert beer_response.status_code == 201

    beer = beer_response.json()

    packaging_format_response = client.post(
        "/packaging-formats/",
        json={
            "code": "BOTTLE-STOCK-TEST",
            "name": "Bottle Stock Test",
            "capacity_liters": "0.500",
        },
    )
    assert packaging_format_response.status_code == 201

    packaging_format = packaging_format_response.json()

    beer_presentation_response = client.post(
        "/beer-presentations/",
        json={
            "code": "IPA-B500-STOCK-TEST",
            "name": "IPA Bottle 500 ml Stock Test",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
        },
    )
    assert beer_presentation_response.status_code == 201

    return beer_presentation_response.json()


def test_stock_movements_update_beer_presentation_stock(client):
    beer_presentation = create_test_beer_presentation(client)

    initial_balance_response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "movement_type": "initial_balance",
            "quantity": 20,
            "reference": "INITIAL-STOCK-TEST",
        },
    )
    assert initial_balance_response.status_code == 201

    sale_response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "movement_type": "sale",
            "quantity": 5,
            "reference": "SALE-STOCK-TEST",
        },
    )
    assert sale_response.status_code == 201

    beer_presentations = client.get("/beer-presentations/").json()
    updated_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == beer_presentation["id"]
    )
    assert updated_presentation["current_stock"] == 15

    movements = client.get(
        f"/beer-presentations/{beer_presentation['id']}/stock-movements"
    ).json()

    assert len(movements) == 2
    assert movements[0]["movement_type"] == "sale"
    assert movements[1]["movement_type"] == "initial_balance"

def test_cannot_create_outbound_movement_with_insufficient_stock(client):
    beer_presentation = create_test_beer_presentation(client)

    response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "movement_type": "sale",
            "quantity": 1,
            "reference": "SALE-NO-STOCK-TEST",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "There is not enough stock for this beer presentation."
    }

    beer_presentations = client.get("/beer-presentations/").json()
    updated_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == beer_presentation["id"]
    )
    assert updated_presentation["current_stock"] == 0

    movements = client.get(
        f"/beer-presentations/{beer_presentation['id']}/stock-movements"
    ).json()
    assert movements == []

def test_cannot_create_packaging_receipt_manually(client):
    beer_presentation = create_test_beer_presentation(client)

    response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "movement_type": "packaging_receipt",
            "quantity": 10,
            "reference": "MANUAL-PACKAGING-RECEIPT",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "Packaging receipts must be registered by a packaging run."
        )
    }

    beer_presentations = client.get("/beer-presentations/").json()
    updated_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == beer_presentation["id"]
    )
    assert updated_presentation["current_stock"] == 0