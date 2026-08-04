from decimal import Decimal


def test_create_packaging_format(client):
    payload = {
        "code": "KEG-50L",
        "name": "Keg 50 L",
        "capacity_liters": "50.000",
        "description": "Barril retornable de 50 litros.",
    }

    response = client.post("/packaging-formats/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["code"] == payload["code"]
    assert data["name"] == payload["name"]
    assert Decimal(data["capacity_liters"]) == Decimal("50.000")
    assert data["description"] == payload["description"]
    assert data["active"] is True

def test_duplicate_packaging_format_code_returns_conflict(client):
    client.post(
        "/packaging-formats/",
        json={
            "code": "KEG-50L",
            "name": "Keg 50 L",
            "capacity_liters": "50.000",
        },
    )

    response = client.post(
        "/packaging-formats/",
        json={
            "code": "KEG-50L",
            "name": "Keg 30 L",
            "capacity_liters": "30.000",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A packaging format with this code already exists."
    }


def test_duplicate_packaging_format_name_returns_conflict(client):
    client.post(
        "/packaging-formats/",
        json={
            "code": "KEG-50L",
            "name": "Keg 50 L",
            "capacity_liters": "50.000",
        },
    )

    response = client.post(
        "/packaging-formats/",
        json={
            "code": "KEG-30L",
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
            "code": "KEG-50L",
            "name": "Keg 50 L",
            "capacity_liters": "50.000",
        },
        {
            "code": "BOT-500ML",
            "name": "Bottle 500 ml",
            "capacity_liters": "0.500",
        },
    ):
        response = client.post("/packaging-formats/", json=payload)
        assert response.status_code == 201

    response = client.get("/packaging-formats/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert {format_["code"] for format_ in data} == {
        "KEG-50L",
        "BOT-500ML",
    }
