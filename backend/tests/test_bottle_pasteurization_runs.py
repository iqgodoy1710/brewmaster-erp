def create_bottle_presentation_with_stock(
    client,
    *,
    stock: int = 100,
):
    beer_response = client.post(
        "/beers/",
        json={
            "name": "Pasteurization Test Beer",
        },
    )
    assert beer_response.status_code == 201
    beer = beer_response.json()

    format_response = client.post(
        "/packaging-formats/",
        json={
            "name": "Pasteurization Bottle 500 ml",
            "capacity_liters": "0.500",
            "format_type": "bottle",
        },
    )
    assert format_response.status_code == 201
    packaging_format = format_response.json()

    presentation_response = client.post(
        "/beer-presentations/",
        json={
            "name": "Pasteurization Bottle Presentation",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
        },
    )
    assert presentation_response.status_code == 201
    presentation = presentation_response.json()

    stock_response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": presentation["id"],
            "movement_type": "initial_balance",
            "quantity": stock,
            "reference": "PASTEURIZATION-INITIAL-STOCK",
        },
    )
    assert stock_response.status_code == 201

    return presentation


def get_presentation(client, presentation_id: int):
    response = client.get("/beer-presentations/")
    assert response.status_code == 200

    return next(
        presentation
        for presentation in response.json()
        if presentation["id"] == presentation_id
    )


def test_pasteurization_deducts_only_waste_from_stock(client):
    presentation = create_bottle_presentation_with_stock(
        client,
        stock=100,
    )

    response = client.post(
        "/bottle-pasteurization-runs/",
        json={
            "beer_presentation_id": presentation["id"],
            "processed_quantity": 80,
            "approved_quantity": 76,
            "notes": "Test pasteurization with waste.",
        },
    )

    assert response.status_code == 201

    pasteurization = response.json()

    assert pasteurization["code"] == "PAS-000001"
    assert pasteurization["processed_quantity"] == 80
    assert pasteurization["approved_quantity"] == 76
    assert pasteurization["waste_quantity"] == 4

    updated_presentation = get_presentation(
        client,
        presentation["id"],
    )
    assert updated_presentation["current_stock"] == 96

    movements_response = client.get(
        (
            f"/beer-presentations/{presentation['id']}"
            "/stock-movements"
        )
    )
    assert movements_response.status_code == 200

    movements = movements_response.json()

    waste_movement = next(
        movement
        for movement in movements
        if movement["movement_type"] == "pasteurization_waste"
    )

    assert waste_movement["quantity"] == 4
    assert (
        waste_movement["pasteurization_run_id"]
        == pasteurization["id"]
    )


def test_pasteurization_without_waste_keeps_stock_unchanged(client):
    presentation = create_bottle_presentation_with_stock(
        client,
        stock=100,
    )

    response = client.post(
        "/bottle-pasteurization-runs/",
        json={
            "beer_presentation_id": presentation["id"],
            "processed_quantity": 80,
            "approved_quantity": 80,
        },
    )

    assert response.status_code == 201
    assert response.json()["waste_quantity"] == 0

    updated_presentation = get_presentation(
        client,
        presentation["id"],
    )
    assert updated_presentation["current_stock"] == 100

    movements_response = client.get(
        (
            f"/beer-presentations/{presentation['id']}"
            "/stock-movements"
        )
    )
    assert movements_response.status_code == 200

    pasteurization_movements = [
        movement
        for movement in movements_response.json()
        if movement["movement_type"] == "pasteurization_waste"
    ]

    assert pasteurization_movements == []


def test_approved_quantity_cannot_exceed_processed_quantity(client):
    presentation = create_bottle_presentation_with_stock(
        client,
        stock=100,
    )

    response = client.post(
        "/bottle-pasteurization-runs/",
        json={
            "beer_presentation_id": presentation["id"],
            "processed_quantity": 80,
            "approved_quantity": 81,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "The approved quantity cannot exceed "
            "the processed quantity."
        )
    }

    updated_presentation = get_presentation(
        client,
        presentation["id"],
    )
    assert updated_presentation["current_stock"] == 100


def test_cannot_pasteurize_more_bottles_than_available(client):
    presentation = create_bottle_presentation_with_stock(
        client,
        stock=50,
    )

    response = client.post(
        "/bottle-pasteurization-runs/",
        json={
            "beer_presentation_id": presentation["id"],
            "processed_quantity": 60,
            "approved_quantity": 58,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "There is not enough bottle stock "
            "for this pasteurization."
        )
    }

    updated_presentation = get_presentation(
        client,
        presentation["id"],
    )
    assert updated_presentation["current_stock"] == 50