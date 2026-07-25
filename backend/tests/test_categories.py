def test_create_category(client):
    response = client.post(
        "/categories/",
        json={
            "name": "Malts",
            "description": "Malt used for brewing.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Malts"
    assert data["description"] == "Malt used for brewing."
    assert data["active"] is True

def test_create_category_with_duplicate_name_returns_conflict(
    client,
):
    category_data = {
        "name": "Malts",
        "description": "Malt used for brewing.",
    }

    client.post("/categories/", json=category_data)

    response = client.post("/categories/", json=category_data)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A category with this name already exists."
    }