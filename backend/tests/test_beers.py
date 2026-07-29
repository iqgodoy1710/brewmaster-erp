def test_create_beer(client):
    payload = {
        "code": "IPA",
        "name": "India Pale Ale",
        "style": "American IPA",
        "description": "Cerveza lupulada.",
    }

    response = client.post("/beers/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["code"] == payload["code"]
    assert data["name"] == payload["name"]
    assert data["style"] == payload["style"]
    assert data["description"] == payload["description"]
    assert data["active"] is True

def test_create_beer_with_duplicate_code_returns_conflict(client):
    first_payload = {
        "code": "IPA",
        "name": "India Pale Ale",
    }
    duplicate_payload = {
        "code": "IPA",
        "name": "West Coast IPA",
    }

    client.post("/beers/", json=first_payload)
    response = client.post("/beers/", json=duplicate_payload)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A beer with this code already exists."
    }

def test_create_beer_with_duplicate_name_returns_conflict(client):
    first_payload = {
        "code": "IPA",
        "name": "India Pale Ale",
    }
    duplicate_payload = {
        "code": "WEST-IPA",
        "name": "India Pale Ale",
    }

    client.post("/beers/", json=first_payload)
    response = client.post("/beers/", json=duplicate_payload)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A beer with this name already exists."
    }

def test_get_beers_returns_active_beers(client):
    client.post(
        "/beers/",
        json={
            "code": "IPA",
            "name": "India Pale Ale",
        },
    )
    client.post(
        "/beers/",
        json={
            "code": "STOUT",
            "name": "Dry Stout",
        },
    )

    response = client.get("/beers/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert {beer["code"] for beer in data} == {"IPA", "STOUT"}