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

from decimal import Decimal


def test_manual_cost_update_creates_cost_history(client):
    category = client.post(
        "/categories/",
        json={"name": "Cost History Category"},
    ).json()

    unit = client.post(
        "/units/",
        json={
            "name": "Cost History Unit",
            "symbol": "chu",
        },
    ).json()

    raw_material = client.post(
        "/raw-materials/",
        json={
            "name": "Cost History Material",
            "category_id": category["id"],
            "unit_id": unit["id"],
            "current_cost": "10.00",
        },
    ).json()

    response = client.patch(
        f"/raw-materials/{raw_material['code']}",
        json={"current_cost": "12.50"},
    )

    assert response.status_code == 200

    history_response = client.get(
        f"/raw-materials/{raw_material['code']}/cost-history"
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["source"] == "manual_update"
    assert history[0]["stock_movement_id"] is None
    assert Decimal(history[0]["previous_cost"]) == Decimal("10.00")
    assert Decimal(history[0]["new_cost"]) == Decimal("12.50")
    assert Decimal(history[0]["variation_amount"]) == Decimal("2.50")
    assert Decimal(history[0]["variation_percentage"]) == Decimal("25.00")