from decimal import Decimal


def test_create_packaging_format(client):
    payload = {
        "name": "Keg 50 L",
        "capacity_liters": "50.000",
        "description": "Barril retornable de 50 litros.",
        "format_type": "keg",
    }

    response = client.post(
        "/packaging-formats/",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["code"] == "FOR-000001"
    assert data["name"] == payload["name"]
    assert Decimal(data["capacity_liters"]) == Decimal("50.000")
    assert data["description"] == payload["description"]
    assert data["format_type"] == "keg"
    assert data["active"] is True


def test_packaging_formats_receive_sequential_generated_codes(client):
    first_response = client.post(
        "/packaging-formats/",
        json={
            "name": "Keg 50 L",
            "capacity_liters": "50.000",
        },
    )
    second_response = client.post(
        "/packaging-formats/",
        json={
            "name": "Bottle 500 ml",
            "capacity_liters": "0.500",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    assert first_response.json()["code"] == "FOR-000001"
    assert second_response.json()["code"] == "FOR-000002"


def test_duplicate_packaging_format_name_returns_conflict(client):
    first_response = client.post(
        "/packaging-formats/",
        json={
            "name": "Keg 50 L",
            "capacity_liters": "50.000",
        },
    )
    assert first_response.status_code == 201

    response = client.post(
        "/packaging-formats/",
        json={
            "name": "Keg 50 L",
            "capacity_liters": "30.000",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A packaging format with this name already exists."
    }


def test_get_packaging_formats_returns_active_formats(client):
    for payload in (
        {
            "name": "Keg 50 L",
            "capacity_liters": "50.000",
            "format_type": "keg",
        },
        {
            "name": "Bottle 500 ml",
            "capacity_liters": "0.500",
            "format_type": "bottle",
        },
    ):
        response = client.post(
            "/packaging-formats/",
            json=payload,
        )
        assert response.status_code == 201

    response = client.get("/packaging-formats/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert {format_["code"] for format_ in data} == {
        "FOR-000001",
        "FOR-000002",
    }