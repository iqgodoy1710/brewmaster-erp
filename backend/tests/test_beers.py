def test_create_beer(client):
    payload = {
        "name": "India Pale Ale",
        "style": "American IPA",
        "description": "Cerveza lupulada.",
    }

    response = client.post("/beers/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["code"] == "CER-000001"
    assert data["name"] == payload["name"]
    assert data["style"] == payload["style"]
    assert data["description"] == payload["description"]
    assert data["active"] is True


def test_beers_receive_sequential_generated_codes(client):
    first_response = client.post(
        "/beers/",
        json={"name": "India Pale Ale"},
    )
    second_response = client.post(
        "/beers/",
        json={"name": "West Coast IPA"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["code"] == "CER-000001"
    assert second_response.json()["code"] == "CER-000002"
    

def test_create_beer_with_duplicate_name_returns_conflict(client):
    first_payload = {
        "name": "India Pale Ale",
    }
    duplicate_payload = {
        "name": "India Pale Ale",
    }

    client.post("/beers/", json=first_payload)
    response = client.post("/beers/", json=duplicate_payload)

    assert response.status_code == 409
    assert response.json() == {"detail": "A beer with this name already exists."}


def test_get_beers_returns_active_beers(client):
    client.post(
        "/beers/",
        json={
            "name": "India Pale Ale",
        },
    )
    client.post(
        "/beers/",
        json={
            "name": "Dry Stout",
        },
    )

    response = client.get("/beers/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert {beer["code"] for beer in data} == {"CER-000001", "CER-000002"}
