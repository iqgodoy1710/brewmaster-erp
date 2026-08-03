from decimal import Decimal


def test_purchase_receipt_increases_raw_material_stock(client):
    category = client.post(
        "/categories/",
        json={"name": "Malts"},
    ).json()

    unit = client.post(
        "/units/",
        json={
            "name": "Kilogram",
            "symbol": "kg",
        },
    ).json()

    supplier = client.post(
        "/suppliers/",
        json={
            "name": "Malt Supply Co.",
            "tax_id": "ESB12345678",
        },
    ).json()

    raw_material = client.post(
        "/raw-materials/",
        json={
            "code": "MALT-001",
            "name": "Pale Ale Malt",
            "category_id": category["id"],
            "unit_id": unit["id"],
            "minimum_stock": 20,
            "current_cost": 0,
        },
    ).json()

    movement_response = client.post(
        "/raw-material-stock-movements/",
        json={
            "raw_material_id": raw_material["id"],
            "supplier_id": supplier["id"],
            "movement_type": "purchase_receipt",
            "quantity": 100,
            "unit_cost": 2.5,
            "reference": "PUR-001",
        },
    )

    assert movement_response.status_code == 201

    movement = movement_response.json()

    assert movement["raw_material_id"] == raw_material["id"]
    assert movement["supplier_id"] == supplier["id"]
    assert movement["movement_type"] == "purchase_receipt"
    assert Decimal(movement["quantity"]) == Decimal("100")

    raw_material_response = client.get(f"/raw-materials/{raw_material['code']}")

    assert raw_material_response.status_code == 200
    assert Decimal(raw_material_response.json()["current_stock"]) == Decimal("100")

    history_response = client.get(f"/raw-material-stock-movements/{raw_material['id']}")

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 1
    assert history[0]["id"] == movement["id"]
    assert history[0]["movement_type"] == "purchase_receipt"


def test_outbound_movement_cannot_make_stock_negative(client):
    category = client.post(
        "/categories/",
        json={"name": "Malts"},
    ).json()

    unit = client.post(
        "/units/",
        json={
            "name": "Kilogram",
            "symbol": "kg",
        },
    ).json()

    raw_material = client.post(
        "/raw-materials/",
        json={
            "code": "MALT-001",
            "name": "Pale Ale Malt",
            "category_id": category["id"],
            "unit_id": unit["id"],
            "minimum_stock": 20,
            "current_cost": 0,
        },
    ).json()

    client.post(
        "/raw-material-stock-movements/",
        json={
            "raw_material_id": raw_material["id"],
            "movement_type": "initial_balance",
            "quantity": 10,
        },
    )

    response = client.post(
        "/raw-material-stock-movements/",
        json={
            "raw_material_id": raw_material["id"],
            "movement_type": "waste",
            "quantity": 11,
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "There is not enough stock for this movement."}

    raw_material_response = client.get(f"/raw-materials/{raw_material['code']}")

    assert Decimal(raw_material_response.json()["current_stock"]) == Decimal("10")
