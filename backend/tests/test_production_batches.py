from decimal import Decimal


def create_test_raw_material(client):
    category_response = client.post(
        "/categories/",
        json={"name": "Malts"},
    )
    assert category_response.status_code == 200

    unit_response = client.post(
        "/units/",
        json={
            "name": "Kilogram",
            "symbol": "kg",
        },
    )
    assert unit_response.status_code == 200

    raw_material_response = client.post(
        "/raw-materials/",
        json={
            "code": "MALT-PALE",
            "name": "Pale Malt",
            "category_id": category_response.json()["id"],
            "unit_id": unit_response.json()["id"],
            "minimum_stock": "0.000",
            "current_cost": "1.25",
        },
    )
    assert raw_material_response.status_code == 200

    return raw_material_response.json()


def create_test_recipe_with_ingredient(client):
    raw_material = create_test_raw_material(client)

    beer_response = client.post(
        "/beers/",
        json={
            "code": "NEIPA",
            "name": "New England IPA",
        },
    )
    assert beer_response.status_code == 201

    recipe_response = client.post(
        "/recipes/",
        json={
            "beer_id": beer_response.json()["id"],
            "version": 1,
            "target_volume_liters": "500.000",
        },
    )
    assert recipe_response.status_code == 201

    recipe = recipe_response.json()

    ingredient_response = client.post(
        "/recipe-ingredients/",
        json={
            "recipe_id": recipe["id"],
            "raw_material_id": raw_material["id"],
            "required_quantity": "100.000",
        },
    )
    assert ingredient_response.status_code == 201

    return recipe


def test_create_production_batch(client):
    recipe = create_test_recipe_with_ingredient(client)

    payload = {
        "code": "PB-IPA-001",
        "recipe_id": recipe["id"],
        "planned_volume_liters": "500.000",
        "notes": "Planificación de lote IPA.",
    }

    response = client.post("/production-batches/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["code"] == payload["code"]
    assert data["recipe_id"] == recipe["id"]
    assert data["planned_volume_liters"] == payload["planned_volume_liters"]
    assert data["notes"] == payload["notes"]
    assert data["status"] == "planned"
    assert Decimal(data["available_bulk_volume_liters"]) == Decimal("0")
    assert data["active"] is True

def test_create_production_batch_without_recipe_ingredients_returns_conflict(
    client,
):
    beer_response = client.post(
        "/beers/",
        json={
            "code": "STOUT",
            "name": "Dry Stout",
        },
    )
    assert beer_response.status_code == 201

    recipe_response = client.post(
        "/recipes/",
        json={
            "beer_id": beer_response.json()["id"],
            "version": 1,
            "target_volume_liters": "500.000",
        },
    )
    assert recipe_response.status_code == 201

    response = client.post(
        "/production-batches/",
        json={
            "code": "PB-STOUT-001",
            "recipe_id": recipe_response.json()["id"],
            "planned_volume_liters": "500.000",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "Cannot plan a production batch for a recipe without ingredients."
        )
    }

def test_duplicate_production_batch_code_returns_conflict(client):
    recipe = create_test_recipe_with_ingredient(client)

    payload = {
        "code": "PB-IPA-001",
        "recipe_id": recipe["id"],
        "planned_volume_liters": "500.000",
    }

    first_response = client.post("/production-batches/", json=payload)
    response = client.post("/production-batches/", json=payload)

    assert first_response.status_code == 201
    assert response.status_code == 409
    assert response.json() == {
        "detail": "A production batch with this code already exists."
    }

def test_get_production_batches_returns_active_batches(client):
    recipe = create_test_recipe_with_ingredient(client)

    create_response = client.post(
        "/production-batches/",
        json={
            "code": "PB-IPA-001",
            "recipe_id": recipe["id"],
            "planned_volume_liters": "500.000",
        },
    )
    assert create_response.status_code == 201

    response = client.get("/production-batches/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "PB-IPA-001"
    assert data[0]["status"] == "planned"

def test_planning_production_batch_does_not_change_raw_material_stock(
    client,
):
    recipe = create_test_recipe_with_ingredient(client)

    raw_material_response = client.get("/raw-materials/MALT-PALE")
    assert raw_material_response.status_code == 200

    raw_material = raw_material_response.json()

    initial_balance_response = client.post(
        "/raw-material-stock-movements/",
        json={
            "raw_material_id": raw_material["id"],
            "movement_type": "initial_balance",
            "quantity": "150.000",
        },
    )
    assert initial_balance_response.status_code == 201

    production_batch_response = client.post(
        "/production-batches/",
        json={
            "code": "PB-IPA-001",
            "recipe_id": recipe["id"],
            "planned_volume_liters": "500.000",
        },
    )
    assert production_batch_response.status_code == 201

    updated_raw_material_response = client.get("/raw-materials/MALT-PALE")
    assert updated_raw_material_response.status_code == 200

    updated_raw_material = updated_raw_material_response.json()
    assert Decimal(updated_raw_material["current_stock"]) == Decimal("150.000")

def test_raw_material_planning_projection_calculates_scaled_consumption(
    client,
):
    recipe = create_test_recipe_with_ingredient(client)

    raw_material_response = client.get("/raw-materials/MALT-PALE")
    assert raw_material_response.status_code == 200

    raw_material = raw_material_response.json()

    initial_balance_response = client.post(
        "/raw-material-stock-movements/",
        json={
            "raw_material_id": raw_material["id"],
            "movement_type": "initial_balance",
            "quantity": "150.000",
        },
    )
    assert initial_balance_response.status_code == 201

    production_batch_response = client.post(
        "/production-batches/",
        json={
            "code": "PB-IPA-001",
            "recipe_id": recipe["id"],
            "planned_volume_liters": "250.000",
        },
    )
    assert production_batch_response.status_code == 201

    response = client.get(
        "/production-batches/planning/raw-material-requirements"
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1

    projection = data[0]
    assert projection["raw_material_id"] == raw_material["id"]
    assert Decimal(projection["current_stock"]) == Decimal("150.000")
    assert Decimal(projection["planned_consumption"]) == Decimal("50.000")
    assert Decimal(projection["projected_available_stock"]) == Decimal("100.000")
    assert projection["has_shortage"] is False


def test_raw_material_planning_projection_detects_shortage(client):
    recipe = create_test_recipe_with_ingredient(client)

    raw_material_response = client.get("/raw-materials/MALT-PALE")
    assert raw_material_response.status_code == 200

    raw_material = raw_material_response.json()

    initial_balance_response = client.post(
        "/raw-material-stock-movements/",
        json={
            "raw_material_id": raw_material["id"],
            "movement_type": "initial_balance",
            "quantity": "50.000",
        },
    )
    assert initial_balance_response.status_code == 201

    production_batch_response = client.post(
        "/production-batches/",
        json={
            "code": "PB-IPA-001",
            "recipe_id": recipe["id"],
            "planned_volume_liters": "500.000",
        },
    )
    assert production_batch_response.status_code == 201

    response = client.get(
        "/production-batches/planning/raw-material-requirements"
    )

    assert response.status_code == 200

    projection = response.json()[0]
    assert Decimal(projection["planned_consumption"]) == Decimal("100.000")
    assert Decimal(projection["projected_available_stock"]) == Decimal("-50.000")
    assert projection["has_shortage"] is True