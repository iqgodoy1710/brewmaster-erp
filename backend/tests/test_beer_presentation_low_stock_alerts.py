def create_test_beer_presentation(
    client,
    suffix: str,
    minimum_stock: int = 0,
):
    beer_response = client.post(
        "/beers/",
        json={
            "code": f"BEER-{suffix}",
            "name": f"Beer Alert {suffix}",
        },
    )
    assert beer_response.status_code == 201

    beer = beer_response.json()

    packaging_format_response = client.post(
        "/packaging-formats/",
        json={
            "code": f"FORMAT-{suffix}",
            "name": f"Format Alert {suffix}",
            "capacity_liters": "0.500",
        },
    )
    assert packaging_format_response.status_code == 201

    packaging_format = packaging_format_response.json()

    presentation_response = client.post(
        "/beer-presentations/",
        json={
            "code": f"PRESENT-{suffix}",
            "name": f"Presentation Alert {suffix}",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
            "minimum_stock": minimum_stock,
        },
    )
    assert presentation_response.status_code == 201

    return presentation_response.json()


def add_initial_stock(
    client,
    beer_presentation_id: int,
    quantity: int,
):
    response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": beer_presentation_id,
            "movement_type": "initial_balance",
            "quantity": quantity,
            "reference": "INITIAL-ALERT-TEST",
        },
    )
    assert response.status_code == 201


def test_beer_presentation_low_stock_alerts_exclude_sufficient_stock(client):
    low_presentation = create_test_beer_presentation(
        client,
        "LOW",
    )

    update_response = client.patch(
        f"/beer-presentations/{low_presentation['code']}/minimum-stock",
        json={
            "minimum_stock": 5,
        },
    )
    assert update_response.status_code == 200

    add_initial_stock(
        client,
        low_presentation["id"],
        3,
    )

    sufficient_presentation = create_test_beer_presentation(
        client,
        "SUFFICIENT",
        minimum_stock=5,
    )
    add_initial_stock(
        client,
        sufficient_presentation["id"],
        6,
    )

    response = client.get("/beer-presentations/low-stock")

    assert response.status_code == 200
    assert response.json() == [
        {
            "beer_presentation_id": low_presentation["id"],
            "beer_presentation_code": low_presentation["code"],
            "beer_presentation_name": low_presentation["name"],
            "current_stock": 3,
            "minimum_stock": 5,
            "shortage_quantity": 2,
        }
    ]


def test_beer_presentation_at_minimum_stock_is_an_alert(client):
    presentation = create_test_beer_presentation(
        client,
        "AT-MINIMUM",
        minimum_stock=5,
    )
    add_initial_stock(
        client,
        presentation["id"],
        5,
    )

    response = client.get("/beer-presentations/low-stock")

    assert response.status_code == 200
    assert response.json() == [
        {
            "beer_presentation_id": presentation["id"],
            "beer_presentation_code": presentation["code"],
            "beer_presentation_name": presentation["name"],
            "current_stock": 5,
            "minimum_stock": 5,
            "shortage_quantity": 0,
        }
    ]