def create_test_raw_material(client):
    category_response = client.post(
        "/categories/",
        json={
            "name": "Malts",
        },
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
            "name": "Pale Malt",
            "category_id": category_response.json()["id"],
            "unit_id": unit_response.json()["id"],
            "minimum_stock": "0.000",
            "current_cost": "1.25",
        },
    )
    assert raw_material_response.status_code == 201

    return raw_material_response.json()


def create_test_recipe(client):
    beer_response = client.post(
        "/beers/",
        json={
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

    return recipe_response.json()


def test_create_recipe_ingredient(client):
    raw_material = create_test_raw_material(client)
    recipe = create_test_recipe(client)

    payload = {
        "recipe_id": recipe["id"],
        "raw_material_id": raw_material["id"],
        "required_quantity": "100.000",
    }

    response = client.post("/recipe-ingredients/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["recipe_id"] == recipe["id"]
    assert data["raw_material_id"] == raw_material["id"]
    assert data["required_quantity"] == payload["required_quantity"]
    assert data["active"] is True


def test_duplicate_recipe_ingredient_returns_conflict(client):
    raw_material = create_test_raw_material(client)
    recipe = create_test_recipe(client)

    payload = {
        "recipe_id": recipe["id"],
        "raw_material_id": raw_material["id"],
        "required_quantity": "100.000",
    }

    first_response = client.post("/recipe-ingredients/", json=payload)
    response = client.post("/recipe-ingredients/", json=payload)

    assert first_response.status_code == 201
    assert response.status_code == 409
    assert response.json() == {
        "detail": "This raw material is already an ingredient of the recipe."
    }


def test_get_recipe_ingredients(client):
    raw_material = create_test_raw_material(client)
    recipe = create_test_recipe(client)

    create_response = client.post(
        "/recipe-ingredients/",
        json={
            "recipe_id": recipe["id"],
            "raw_material_id": raw_material["id"],
            "required_quantity": "100.000",
        },
    )
    assert create_response.status_code == 201

    response = client.get(f"/recipes/{recipe['id']}/ingredients")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["recipe_id"] == recipe["id"]
    assert data[0]["raw_material_id"] == raw_material["id"]
    assert data[0]["required_quantity"] == "100.000"


def test_get_ingredients_for_missing_recipe_returns_not_found(client):
    response = client.get("/recipes/999/ingredients")

    assert response.status_code == 404
    assert response.json() == {"detail": "The recipe does not exist."}


def test_update_recipe_ingredient_changes_material_and_quantity(client):
    raw_material = create_test_raw_material(client)
    recipe = create_test_recipe(client)

    ingredient_response = client.post(
        "/recipe-ingredients/",
        json={
            "recipe_id": recipe["id"],
            "raw_material_id": raw_material["id"],
            "required_quantity": "100.000",
        },
    )
    assert ingredient_response.status_code == 201

    second_raw_material_response = client.post(
        "/raw-materials/",
        json={
            "name": "Munich Malt",
            "category_id": raw_material["category_id"],
            "unit_id": raw_material["unit_id"],
            "minimum_stock": "0.000",
            "current_cost": "1.50",
        },
    )
    assert second_raw_material_response.status_code == 201

    second_raw_material = second_raw_material_response.json()

    response = client.patch(
        f"/recipe-ingredients/{ingredient_response.json()['id']}",
        json={
            "raw_material_id": second_raw_material["id"],
            "required_quantity": "80.000",
        },
    )

    assert response.status_code == 200
    assert response.json()["raw_material_id"] == second_raw_material["id"]
    assert response.json()["required_quantity"] == "80.000"


def test_deactivate_recipe_ingredient_hides_it_and_allows_reactivation(client):
    raw_material = create_test_raw_material(client)
    recipe = create_test_recipe(client)

    ingredient_response = client.post(
        "/recipe-ingredients/",
        json={
            "recipe_id": recipe["id"],
            "raw_material_id": raw_material["id"],
            "required_quantity": "100.000",
        },
    )
    assert ingredient_response.status_code == 201

    ingredient = ingredient_response.json()

    delete_response = client.delete(f"/recipe-ingredients/{ingredient['id']}")

    assert delete_response.status_code == 200
    assert delete_response.json()["active"] is False

    list_response = client.get(f"/recipes/{recipe['id']}/ingredients")

    assert list_response.status_code == 200
    assert list_response.json() == []

    recreate_response = client.post(
        "/recipe-ingredients/",
        json={
            "recipe_id": recipe["id"],
            "raw_material_id": raw_material["id"],
            "required_quantity": "75.000",
        },
    )

    assert recreate_response.status_code == 201
    assert recreate_response.json()["id"] == ingredient["id"]
    assert recreate_response.json()["active"] is True
    assert recreate_response.json()["required_quantity"] == "75.000"
