from decimal import Decimal


def create_raw_material(
    client,
    code: str,
    name: str,
    category_id: int,
    unit_id: int,
):
    response = client.post(
        "/raw-materials/",
        json={
            "code": code,
            "name": name,
            "category_id": category_id,
            "unit_id": unit_id,
            "minimum_stock": "0.000",
            "current_cost": "0.000",
        },
    )

    assert response.status_code == 201

    return response.json()


def add_initial_stock(
    client,
    raw_material_id: int,
    quantity: str,
):
    response = client.post(
        "/raw-material-stock-movements/",
        json={
            "raw_material_id": raw_material_id,
            "movement_type": "initial_balance",
            "quantity": quantity,
        },
    )

    assert response.status_code == 201


def create_completed_batch_with_presentation(client):
    category = client.post(
        "/categories/",
        json={"name": "Ingredients and Packaging"},
    ).json()

    unit = client.post(
        "/units/",
        json={
            "name": "Unit",
            "symbol": "u",
        },
    ).json()

    malt = create_raw_material(
        client,
        "MALT-IPA-TEST",
        "IPA Test Malt",
        category["id"],
        unit["id"],
    )
    add_initial_stock(client, malt["id"], "100.000")

    bottle = create_raw_material(
        client,
        "BOTTLE-500-TEST",
        "Test Bottle 500 ml",
        category["id"],
        unit["id"],
    )
    cap = create_raw_material(
        client,
        "CAP-TEST",
        "Test Crown Cap",
        category["id"],
        unit["id"],
    )
    label = create_raw_material(
        client,
        "LABEL-TEST",
        "Test Bottle Label",
        category["id"],
        unit["id"],
    )

    for packaging_material in (bottle, cap, label):
        add_initial_stock(
            client,
            packaging_material["id"],
            "100.000",
        )

    beer = client.post(
        "/beers/",
        json={
            "code": "IPA-TEST",
            "name": "IPA Test Beer",
        },
    ).json()

    recipe = client.post(
        "/recipes/",
        json={
            "beer_id": beer["id"],
            "version": 1,
            "target_volume_liters": "100.000",
        },
    ).json()

    recipe_ingredient_response = client.post(
        "/recipe-ingredients/",
        json={
            "recipe_id": recipe["id"],
            "raw_material_id": malt["id"],
            "required_quantity": "10.000",
        },
    )
    assert recipe_ingredient_response.status_code == 201

    production_batch = client.post(
        "/production-batches/",
        json={
            "code": "PB-IPA-TEST",
            "recipe_id": recipe["id"],
            "planned_volume_liters": "100.000",
        },
    ).json()

    completion_response = client.post(
        f"/production-batches/{production_batch['code']}/complete",
        json={"produced_volume_liters": "100.000"},
    )
    assert completion_response.status_code == 200

    packaging_format = client.post(
        "/packaging-formats/",
        json={
            "code": "BOTTLE-500-TEST",
            "name": "Test Bottle 500 ml",
            "capacity_liters": "0.500",
        },
    ).json()

    beer_presentation = client.post(
        "/beer-presentations/",
        json={
            "code": "IPA-B500-TEST",
            "name": "IPA Test Bottle 500 ml",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
        },
    ).json()

    for packaging_material in (bottle, cap, label):
        response = client.post(
            "/beer-presentation-packaging-materials/",
            json={
                "beer_presentation_id": beer_presentation["id"],
                "raw_material_id": packaging_material["id"],
                "required_quantity": "1.000",
            },
        )
        assert response.status_code == 201

    return {
        "production_batch": production_batch,
        "beer_presentation": beer_presentation,
        "packaging_materials": (bottle, cap, label),
    }


def test_create_packaging_run_consumes_bulk_beer_and_materials(client):
    data = create_completed_batch_with_presentation(client)

    response = client.post(
        "/packaging-runs/",
        json={
            "code": "PACK-IPA-TEST-001",
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 10,
        },
    )

    assert response.status_code == 201

    packaging_run = response.json()

    assert Decimal(packaging_run["packaged_volume_liters"]) == Decimal("5.000")

    production_batches = client.get("/production-batches/").json()
    production_batch = next(
        batch
        for batch in production_batches
        if batch["id"] == data["production_batch"]["id"]
    )
    assert Decimal(production_batch["available_bulk_volume_liters"]) == Decimal(
        "95.000"
    )

    beer_presentations = client.get("/beer-presentations/").json()
    beer_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == data["beer_presentation"]["id"]
    )
    assert beer_presentation["current_stock"] == 10

    raw_materials = client.get("/raw-materials/").json()
    stock_by_id = {
        raw_material["id"]: Decimal(raw_material["current_stock"])
        for raw_material in raw_materials
    }

    for packaging_material in data["packaging_materials"]:
        assert stock_by_id[packaging_material["id"]] == Decimal("90.000")

        movements = client.get(
            f"/raw-material-stock-movements/{packaging_material['id']}"
        ).json()

        assert movements[0]["packaging_run_id"] == packaging_run["id"]
        assert movements[0]["reference"] == packaging_run["code"]


def test_cannot_create_packaging_run_with_duplicate_code(client):
    data = create_completed_batch_with_presentation(client)

    payload = {
        "code": "PACK-IPA-TEST-001",
        "production_batch_id": data["production_batch"]["id"],
        "beer_presentation_id": data["beer_presentation"]["id"],
        "packaged_quantity": 10,
    }

    first_response = client.post(
        "/packaging-runs/",
        json=payload,
    )
    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/packaging-runs/",
        json=payload,
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": "A packaging run with this code already exists."
    }


def test_cannot_package_more_bulk_beer_than_available(client):
    data = create_completed_batch_with_presentation(client)

    response = client.post(
        "/packaging-runs/",
        json={
            "code": "PACK-IPA-TEST-OVERFLOW",
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 201,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "There is not enough bulk beer available "
            "for this packaging run."
        )
    }

    production_batches = client.get("/production-batches/").json()
    production_batch = next(
        batch
        for batch in production_batches
        if batch["id"] == data["production_batch"]["id"]
    )
    assert Decimal(
        production_batch["available_bulk_volume_liters"]
    ) == Decimal("100.000")

    beer_presentations = client.get("/beer-presentations/").json()
    beer_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == data["beer_presentation"]["id"]
    )
    assert beer_presentation["current_stock"] == 0

    raw_materials = client.get("/raw-materials/").json()
    stock_by_id = {
        raw_material["id"]: Decimal(raw_material["current_stock"])
        for raw_material in raw_materials
    }

    for packaging_material in data["packaging_materials"]:
        assert stock_by_id[packaging_material["id"]] == Decimal(
            "100.000"
        )

    assert client.get("/packaging-runs/").json() == []


def test_cannot_package_when_packaging_material_stock_is_insufficient(client):
    data = create_completed_batch_with_presentation(client)

    response = client.post(
        "/packaging-runs/",
        json={
            "code": "PACK-IPA-TEST-NO-MATERIAL",
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 101,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "There is not enough stock for a packaging material."
    }

    production_batches = client.get("/production-batches/").json()
    production_batch = next(
        batch
        for batch in production_batches
        if batch["id"] == data["production_batch"]["id"]
    )
    assert Decimal(
        production_batch["available_bulk_volume_liters"]
    ) == Decimal("100.000")

    beer_presentations = client.get("/beer-presentations/").json()
    beer_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == data["beer_presentation"]["id"]
    )
    assert beer_presentation["current_stock"] == 0

    raw_materials = client.get("/raw-materials/").json()
    stock_by_id = {
        raw_material["id"]: Decimal(raw_material["current_stock"])
        for raw_material in raw_materials
    }

    for packaging_material in data["packaging_materials"]:
        assert stock_by_id[packaging_material["id"]] == Decimal(
            "100.000"
        )

    assert client.get("/packaging-runs/").json() == []


def test_cannot_package_a_batch_that_is_not_completed(client):
    data = create_completed_batch_with_presentation(client)

    planned_batch_response = client.post(
        "/production-batches/",
        json={
            "code": "PB-IPA-TEST-PLANNED",
            "recipe_id": data["production_batch"]["recipe_id"],
            "planned_volume_liters": "100.000",
        },
    )
    assert planned_batch_response.status_code == 201

    planned_batch = planned_batch_response.json()

    response = client.post(
        "/packaging-runs/",
        json={
            "code": "PACK-IPA-TEST-PLANNED",
            "production_batch_id": planned_batch["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 10,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Only completed production batches can be packaged."
    }

    assert client.get("/packaging-runs/").json() == []


def test_cannot_package_with_presentation_from_another_beer(client):
    data = create_completed_batch_with_presentation(client)

    other_beer_response = client.post(
        "/beers/",
        json={
            "code": "STOUT-TEST",
            "name": "Stout Test Beer",
        },
    )
    assert other_beer_response.status_code == 201

    other_beer = other_beer_response.json()

    other_format_response = client.post(
        "/packaging-formats/",
        json={
            "code": "CAN-500-TEST",
            "name": "Test Can 500 ml",
            "capacity_liters": "0.500",
        },
    )
    assert other_format_response.status_code == 201

    other_format = other_format_response.json()

    other_presentation_response = client.post(
        "/beer-presentations/",
        json={
            "code": "STOUT-C500-TEST",
            "name": "Stout Test Can 500 ml",
            "beer_id": other_beer["id"],
            "packaging_format_id": other_format["id"],
        },
    )
    assert other_presentation_response.status_code == 201

    other_presentation = other_presentation_response.json()

    response = client.post(
        "/packaging-runs/",
        json={
            "code": "PACK-IPA-TEST-WRONG-BEER",
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": other_presentation["id"],
            "packaged_quantity": 10,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "The beer presentation does not match "
            "the production batch beer."
        )
    }

    assert client.get("/packaging-runs/").json() == []