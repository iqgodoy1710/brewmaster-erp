def create_test_beer(client):
    response = client.post(
        "/beers/",
        json={
            "name": "New England IPA",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_recipe(client):
    beer = create_test_beer(client)

    payload = {
        "beer_id": beer["id"],
        "version": 1,
        "target_volume_liters": "500.000",
        "notes": "Receta base para lote piloto.",
    }

    response = client.post("/recipes/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["beer_id"] == beer["id"]
    assert data["version"] == payload["version"]
    assert data["target_volume_liters"] == payload["target_volume_liters"]
    assert data["notes"] == payload["notes"]
    assert data["active"] is True
    assert data["is_current"] is True


def test_create_recipe_for_missing_beer_returns_not_found(client):
    response = client.post(
        "/recipes/",
        json={
            "beer_id": 999,
            "version": 1,
            "target_volume_liters": "500.000",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "The beer does not exist."}


def test_create_recipe_with_duplicate_version_returns_conflict(client):
    beer = create_test_beer(client)

    payload = {
        "beer_id": beer["id"],
        "version": 1,
        "target_volume_liters": "500.000",
    }

    first_response = client.post("/recipes/", json=payload)
    response = client.post("/recipes/", json=payload)

    assert first_response.status_code == 201
    assert response.status_code == 409
    assert response.json() == {
        "detail": "A recipe with this beer and version already exists."
    }


def test_get_recipes_returns_active_recipes(client):
    beer = create_test_beer(client)

    for version in (1, 2):
        response = client.post(
            "/recipes/",
            json={
                "beer_id": beer["id"],
                "version": version,
                "target_volume_liters": "500.000",
            },
        )
        assert response.status_code == 201

    response = client.get("/recipes/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert {recipe["version"] for recipe in data} == {1, 2}


def test_update_recipe_without_production_batches(client):
    beer = create_test_beer(client)

    create_response = client.post(
        "/recipes/",
        json={
            "beer_id": beer["id"],
            "version": 1,
            "target_volume_liters": "500.000",
            "notes": "Original.",
        },
    )

    assert create_response.status_code == 201

    recipe = create_response.json()

    response = client.patch(
        f"/recipes/{recipe['id']}",
        json={
            "target_volume_liters": "600.000",
            "notes": "Volumen corregido.",
        },
    )

    assert response.status_code == 200
    assert response.json()["target_volume_liters"] == "600.000"
    assert response.json()["notes"] == "Volumen corregido."


def test_new_recipe_does_not_replace_current_recipe_by_default(
    client,
):
    beer = create_test_beer(client)

    first_response = client.post(
        "/recipes/",
        json={
            "beer_id": beer["id"],
            "version": 1,
            "target_volume_liters": "500.000",
        },
    )
    assert first_response.status_code == 201
    assert first_response.json()["is_current"] is True

    second_response = client.post(
        "/recipes/",
        json={
            "beer_id": beer["id"],
            "version": 2,
            "target_volume_liters": "500.000",
        },
    )
    assert second_response.status_code == 201
    assert second_response.json()["is_current"] is False

    recipes = client.get("/recipes/").json()

    current_recipes = [recipe for recipe in recipes if recipe["is_current"]]

    assert len(current_recipes) == 1
    assert current_recipes[0]["version"] == 1


def test_recipe_can_be_created_as_current(client):
    beer = create_test_beer(client)

    first_response = client.post(
        "/recipes/",
        json={
            "beer_id": beer["id"],
            "version": 1,
            "target_volume_liters": "500.000",
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/recipes/",
        json={
            "beer_id": beer["id"],
            "version": 2,
            "target_volume_liters": "600.000",
            "is_current": True,
        },
    )
    assert second_response.status_code == 201
    assert second_response.json()["is_current"] is True

    recipes = client.get("/recipes/").json()

    recipe_by_version = {recipe["version"]: recipe for recipe in recipes}

    assert recipe_by_version[1]["is_current"] is False
    assert recipe_by_version[2]["is_current"] is True


def test_existing_recipe_can_be_selected_as_current(client):
    beer = create_test_beer(client)

    first_recipe = client.post(
        "/recipes/",
        json={
            "beer_id": beer["id"],
            "version": 1,
            "target_volume_liters": "500.000",
        },
    ).json()

    second_recipe = client.post(
        "/recipes/",
        json={
            "beer_id": beer["id"],
            "version": 2,
            "target_volume_liters": "600.000",
        },
    ).json()

    response = client.patch(f"/recipes/{second_recipe['id']}/set-current")

    assert response.status_code == 200
    assert response.json()["is_current"] is True

    recipes = client.get("/recipes/").json()

    recipe_by_id = {recipe["id"]: recipe for recipe in recipes}

    assert recipe_by_id[first_recipe["id"]]["is_current"] is False
    assert recipe_by_id[second_recipe["id"]]["is_current"] is True
