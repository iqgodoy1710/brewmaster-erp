def create_test_beer(client):
    response = client.post(
        "/beers/",
        json={
            "code": "IPA",
            "name": "India Pale Ale",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_packaging_format(client):
    response = client.post(
        "/packaging-formats/",
        json={
            "code": "KEG-50L",
            "name": "Keg 50 L",
            "capacity_liters": "50.000",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_beer_presentation(client):
    beer = create_test_beer(client)
    packaging_format = create_test_packaging_format(client)

    payload = {
        "code": "IPA-KEG-50L",
        "name": "IPA - Keg 50 L",
        "beer_id": beer["id"],
        "packaging_format_id": packaging_format["id"],
        "description": "IPA en barril retornable.",
    }

    response = client.post("/beer-presentations/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["code"] == payload["code"]
    assert data["name"] == payload["name"]
    assert data["beer_id"] == beer["id"]
    assert data["packaging_format_id"] == packaging_format["id"]
    assert data["active"] is True


def test_duplicate_beer_presentation_combination_returns_conflict(client):
    beer = create_test_beer(client)
    packaging_format = create_test_packaging_format(client)

    first_response = client.post(
        "/beer-presentations/",
        json={
            "code": "IPA-KEG-50L",
            "name": "IPA - Keg 50 L",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
        },
    )
    response = client.post(
        "/beer-presentations/",
        json={
            "code": "IPA-KEG-50L-ALT",
            "name": "IPA - Keg 50 L Alternative",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
        },
    )

    assert first_response.status_code == 201
    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "A presentation already exists for this beer and packaging format."
        )
    }


def test_get_beer_presentations_returns_active_presentations(client):
    beer = create_test_beer(client)

    keg_format = create_test_packaging_format(client)
    bottle_format_response = client.post(
        "/packaging-formats/",
        json={
            "code": "BOT-500ML",
            "name": "Bottle 500 ml",
            "capacity_liters": "0.500",
        },
    )
    assert bottle_format_response.status_code == 201
    bottle_format = bottle_format_response.json()

    for payload in (
        {
            "code": "IPA-KEG-50L",
            "name": "IPA - Keg 50 L",
            "beer_id": beer["id"],
            "packaging_format_id": keg_format["id"],
        },
        {
            "code": "IPA-BOT-500ML",
            "name": "IPA - Bottle 500 ml",
            "beer_id": beer["id"],
            "packaging_format_id": bottle_format["id"],
        },
    ):
        response = client.post("/beer-presentations/", json=payload)
        assert response.status_code == 201

    response = client.get("/beer-presentations/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert {presentation["code"] for presentation in data} == {
        "IPA-KEG-50L",
        "IPA-BOT-500ML",
    }


def test_create_beer_presentation_for_missing_packaging_format_returns_not_found(
    client,
):
    beer = create_test_beer(client)

    response = client.post(
        "/beer-presentations/",
        json={
            "code": "IPA-MISSING-FORMAT",
            "name": "IPA - Missing Format",
            "beer_id": beer["id"],
            "packaging_format_id": 999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "The packaging format does not exist."
    }