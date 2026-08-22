def test_create_raw_material(client):
    category_response = client.post(
        "/categories/",
        json={
            "name": "Malts",
            "description": "Malt used for brewing.",
        },
    )
    category_id = category_response.json()["id"]

    unit_response = client.post(
        "/units/",
        json={
            "name": "Kilogram",
            "symbol": "kg",
        },
    )
    unit_id = unit_response.json()["id"]

    response = client.post(
        "/raw-materials/",
        json={
            
            "name": "Pale Ale Malt",
            "category_id": category_id,
            "unit_id": unit_id,
            "minimum_stock": 20,
            "current_cost": 2.5,
            "description": "Base malt.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["code"] == "INS-000001"
    assert data["name"] == "Pale Ale Malt"
    assert data["category_id"] == category_id
    assert data["unit_id"] == unit_id
    assert data["active"] is True