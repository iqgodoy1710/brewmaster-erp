from decimal import Decimal


def create_test_raw_material(
    client,
    code: str,
    name: str,
    category_id: int,
    unit_id: int,
    minimum_stock: str,
):
    response = client.post(
        "/raw-materials/",
        json={
            
            "name": name,
            "category_id": category_id,
            "unit_id": unit_id,
            "minimum_stock": minimum_stock,
            "current_cost": "0.000",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_get_raw_material_low_stock_alerts(client):
    category = client.post(
        "/categories/",
        json={"name": "Alert Test Category"},
    ).json()

    unit = client.post(
        "/units/",
        json={
            "name": "Alert Test Unit",
            "symbol": "atu",
        },
    ).json()

    low_stock_material = create_test_raw_material(
        client,
        "LOW-STOCK-TEST",
        "Low Stock Test Material",
        category["id"],
        unit["id"],
        "10.000",
    )

    sufficient_stock_material = create_test_raw_material(
        client,
        "ENOUGH-STOCK-TEST",
        "Enough Stock Test Material",
        category["id"],
        unit["id"],
        "10.000",
    )

    stock_movement_response = client.post(
        "/raw-material-stock-movements/",
        json={
            "raw_material_id": sufficient_stock_material["id"],
            "movement_type": "initial_balance",
            "quantity": "20.000",
        },
    )
    assert stock_movement_response.status_code == 201

    response = client.get("/raw-materials/low-stock")

    assert response.status_code == 200

    alerts = response.json()

    assert len(alerts) == 1
    assert alerts[0]["raw_material_id"] == low_stock_material["id"]
    assert alerts[0]["raw_material_code"] == low_stock_material["code"]
    assert Decimal(alerts[0]["current_stock"]) == Decimal("0.000")
    assert Decimal(alerts[0]["minimum_stock"]) == Decimal("10.000")
    assert Decimal(alerts[0]["shortage_quantity"]) == Decimal("10.000")


def test_raw_material_at_minimum_stock_is_in_alerts(client):
    category = client.post(
        "/categories/",
        json={"name": "Threshold Alert Test Category"},
    ).json()

    unit = client.post(
        "/units/",
        json={
            "name": "Threshold Alert Test Unit",
            "symbol": "tatu",
        },
    ).json()

    raw_material = create_test_raw_material(
        client,
        "THRESHOLD-STOCK-TEST",
        "Threshold Stock Test Material",
        category["id"],
        unit["id"],
        "10.000",
    )

    stock_movement_response = client.post(
        "/raw-material-stock-movements/",
        json={
            "raw_material_id": raw_material["id"],
            "movement_type": "initial_balance",
            "quantity": "10.000",
        },
    )
    assert stock_movement_response.status_code == 201

    alerts = client.get("/raw-materials/low-stock").json()

    assert len(alerts) == 1
    assert alerts[0]["raw_material_id"] == raw_material["id"]
    assert Decimal(alerts[0]["shortage_quantity"]) == Decimal("0.000")