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


def create_completed_batch_with_presentation(
    client, packaging_format_type: str = "keg", capacity_liters: str = "0.500"
):
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
            "name": "Test Bottle 500 ml",
            "capacity_liters": capacity_liters,
            "format_type": packaging_format_type,
        },
    ).json()

    beer_presentation = client.post(
        "/beer-presentations/",
        json={
            "name": "IPA Test Bottle 500 ml",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
        },
    ).json()

    packaging_materials = (bottle, cap, label)

    if packaging_format_type != "keg":
        for packaging_material in packaging_materials:
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
        "packaging_materials": packaging_materials,
    }


def test_create_packaging_run_consumes_bulk_beer_without_consuming_materials(
    client,
):
    data = create_completed_batch_with_presentation(client)

    response = client.post(
        "/packaging-runs/",
        json={
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
        assert stock_by_id[packaging_material["id"]] == Decimal("100.000")

    finished_product_movements = client.get(
        f"/beer-presentations/{data['beer_presentation']['id']}/stock-movements"
    ).json()

    assert len(finished_product_movements) == 1
    assert finished_product_movements[0]["movement_type"] == "packaging_receipt"
    assert finished_product_movements[0]["packaging_run_id"] == packaging_run["id"]
    assert finished_product_movements[0]["quantity"] == 10
    assert finished_product_movements[0]["reference"] == packaging_run["code"]


def test_packaging_runs_receive_sequential_generated_codes(client):
    data = create_completed_batch_with_presentation(client)

    first_response = client.post(
        "/packaging-runs/",
        json={
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 10,
        },
    )
    second_response = client.post(
        "/packaging-runs/",
        json={
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 10,
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    assert first_response.json()["code"] == "ENV-000001"
    assert second_response.json()["code"] == "ENV-000002"


def test_cannot_package_more_bulk_beer_than_available(client):
    data = create_completed_batch_with_presentation(client)

    response = client.post(
        "/packaging-runs/",
        json={
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 201,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": ("There is not enough bulk beer available for this packaging run.")
    }

    production_batches = client.get("/production-batches/").json()
    production_batch = next(
        batch
        for batch in production_batches
        if batch["id"] == data["production_batch"]["id"]
    )
    assert Decimal(production_batch["available_bulk_volume_liters"]) == Decimal(
        "100.000"
    )

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
        assert stock_by_id[packaging_material["id"]] == Decimal("100.000")

    assert client.get("/packaging-runs/").json() == []


def test_packaging_keg_does_not_consume_packaging_materials(client):
    data = create_completed_batch_with_presentation(client)

    response = client.post(
        "/packaging-runs/",
        json={
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 101,
        },
    )

    assert response.status_code == 201

    production_batches = client.get("/production-batches/").json()
    production_batch = next(
        batch
        for batch in production_batches
        if batch["id"] == data["production_batch"]["id"]
    )
    assert Decimal(production_batch["available_bulk_volume_liters"]) == Decimal(
        "49.500"
    )

    beer_presentations = client.get("/beer-presentations/").json()
    beer_presentation = next(
        presentation
        for presentation in beer_presentations
        if presentation["id"] == data["beer_presentation"]["id"]
    )
    assert beer_presentation["current_stock"] == 101

    raw_materials = client.get("/raw-materials/").json()
    stock_by_id = {
        raw_material["id"]: Decimal(raw_material["current_stock"])
        for raw_material in raw_materials
    }

    for packaging_material in data["packaging_materials"]:
        assert stock_by_id[packaging_material["id"]] == Decimal("100.000")

    assert len(client.get("/packaging-runs/").json()) == 1


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
            "production_batch_id": planned_batch["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 10,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Only completed or in-progress production batches can be packaged."
    }

    assert client.get("/packaging-runs/").json() == []


def test_cannot_package_with_presentation_from_another_beer(client):
    data = create_completed_batch_with_presentation(client)

    other_beer_response = client.post(
        "/beers/",
        json={
            "name": "Stout Test Beer",
        },
    )
    assert other_beer_response.status_code == 201

    other_beer = other_beer_response.json()

    other_format_response = client.post(
        "/packaging-formats/",
        json={
            "name": "Test Can 500 ml",
            "capacity_liters": "0.500",
        },
    )
    assert other_format_response.status_code == 201

    other_format = other_format_response.json()

    other_presentation_response = client.post(
        "/beer-presentations/",
        json={
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
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": other_presentation["id"],
            "packaged_quantity": 10,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": ("The beer presentation does not match the production batch beer.")
    }

    assert client.get("/packaging-runs/").json() == []


def test_fill_keg_from_packaging_run_creates_traceability(client):
    data = create_completed_batch_with_presentation(
        client,
        packaging_format_type="keg",
    )

    packaging_run_response = client.post(
        "/packaging-runs/",
        json={
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 1,
        },
    )
    assert packaging_run_response.status_code == 201

    packaging_run = packaging_run_response.json()

    keg_response = client.post(
        "/kegs/",
        json={
            "code": "K20-F-001",
            "packaging_format_id": data["beer_presentation"]["packaging_format_id"],
            "form_factor": "flat",
        },
    )
    assert keg_response.status_code == 201

    keg = keg_response.json()

    filling_response = client.post(
        "/keg-movements/fill",
        json={
            "keg_id": keg["id"],
            "packaging_run_id": packaging_run["id"],
        },
    )

    assert filling_response.status_code == 201

    filling = filling_response.json()

    assert filling["movement_type"] == "filling"
    assert filling["previous_status"] == "clean_available"
    assert filling["new_status"] == "filled"
    assert filling["keg_id"] == keg["id"]
    assert filling["packaging_run_id"] == packaging_run["id"]

    kegs_response = client.get("/kegs/")
    assert kegs_response.status_code == 200

    updated_keg = kegs_response.json()[0]

    assert updated_keg["status"] == "filled"
    assert updated_keg["beer_presentation_id"] == data["beer_presentation"]["id"]
    assert updated_keg["production_batch_id"] == data["production_batch"]["id"]

    movements_response = client.get(f"/kegs/{keg['id']}/movements")
    assert movements_response.status_code == 200
    assert len(movements_response.json()) == 1


def test_completing_keg_sale_delivers_the_assigned_keg(client):
    data = create_completed_batch_with_presentation(
        client,
        packaging_format_type="keg",
    )

    packaging_run_response = client.post(
        "/packaging-runs/",
        json={
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 1,
        },
    )
    assert packaging_run_response.status_code == 201

    packaging_run = packaging_run_response.json()

    keg_response = client.post(
        "/kegs/",
        json={
            "code": "K20-F-SALE-001",
            "packaging_format_id": data["beer_presentation"]["packaging_format_id"],
            "form_factor": "flat",
        },
    )
    assert keg_response.status_code == 201

    keg = keg_response.json()

    fill_response = client.post(
        "/keg-movements/fill",
        json={
            "keg_id": keg["id"],
            "packaging_run_id": packaging_run["id"],
        },
    )
    assert fill_response.status_code == 201

    price_response = client.post(
        "/beer-presentation-prices/",
        json={
            "beer_presentation_id": data["beer_presentation"]["id"],
            "unit_price": "100.00",
        },
    )
    assert price_response.status_code == 201

    customer_response = client.post(
        "/customers/",
        json={
            "name": "Keg Sale Customer",
        },
    )
    assert customer_response.status_code == 201

    customer = customer_response.json()

    sale_response = client.post(
        "/sales/",
        json={
            "customer_id": customer["id"],
        },
    )
    assert sale_response.status_code == 201

    sale = sale_response.json()

    sale_item_response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "quantity": 1,
        },
    )
    assert sale_item_response.status_code == 201

    completion_response = client.post(
        f"/sales/{sale['code']}/complete",
        json={
            "keg_ids": [keg["id"]],
        },
    )
    assert completion_response.status_code == 200
    assert completion_response.json()["status"] == "completed"

    updated_keg = client.get("/kegs/").json()[0]

    assert updated_keg["status"] == "at_customer"
    assert updated_keg["customer_id"] == customer["id"]

    movements = client.get(f"/kegs/{keg['id']}/movements").json()

    assert any(
        movement["movement_type"] == "delivery"
        and movement["sale_id"] == sale["id"]
        and movement["customer_id"] == customer["id"]
        for movement in movements
    )


def create_delivered_kegs(
    client,
    quantity: int = 1,
):
    data = create_completed_batch_with_presentation(
        client,
        packaging_format_type="keg",
    )

    packaging_run_response = client.post(
        "/packaging-runs/",
        json={
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": quantity,
        },
    )
    assert packaging_run_response.status_code == 201

    packaging_run = packaging_run_response.json()

    kegs = []

    for index in range(1, quantity + 1):
        keg_response = client.post(
            "/kegs/",
            json={
                "code": f"K20-LIFECYCLE-{index:03d}",
                "packaging_format_id": (
                    data["beer_presentation"]["packaging_format_id"]
                ),
                "form_factor": "flat",
            },
        )
        assert keg_response.status_code == 201

        keg = keg_response.json()

        filling_response = client.post(
            "/keg-movements/fill",
            json={
                "keg_id": keg["id"],
                "packaging_run_id": packaging_run["id"],
            },
        )
        assert filling_response.status_code == 201

        kegs.append(keg)

    price_response = client.post(
        "/beer-presentation-prices/",
        json={
            "beer_presentation_id": data["beer_presentation"]["id"],
            "unit_price": "100.00",
        },
    )
    assert price_response.status_code == 201

    customer_response = client.post(
        "/customers/",
        json={
            "name": "Keg Lifecycle Customer",
        },
    )
    assert customer_response.status_code == 201

    customer = customer_response.json()

    sale_response = client.post(
        "/sales/",
        json={
            "customer_id": customer["id"],
        },
    )
    assert sale_response.status_code == 201

    sale = sale_response.json()

    sale_item_response = client.post(
        "/sale-items/",
        json={
            "sale_id": sale["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "quantity": quantity,
        },
    )
    assert sale_item_response.status_code == 201

    completion_response = client.post(
        f"/sales/{sale['code']}/complete",
        json={
            "keg_ids": [keg["id"] for keg in kegs],
        },
    )
    assert completion_response.status_code == 200

    return {
        "data": data,
        "customer": customer,
        "sale": sale,
        "kegs": kegs,
    }


def get_keg_by_id(client, keg_id: int):
    response = client.get("/kegs/")
    assert response.status_code == 200

    return next(keg for keg in response.json() if keg["id"] == keg_id)


def test_returning_empty_keg_marks_it_as_dirty(client):
    result = create_delivered_kegs(client)

    keg = result["kegs"][0]

    response = client.post(
        "/keg-movements/return",
        json={
            "keg_id": keg["id"],
            "resulting_volume_liters": "0.000",
        },
    )

    assert response.status_code == 201

    movement = response.json()

    assert movement["movement_type"] == "return"
    assert movement["previous_status"] == "at_customer"
    assert movement["new_status"] == "dirty"
    assert Decimal(movement["resulting_volume_liters"]) == Decimal("0.000")

    updated_keg = get_keg_by_id(client, keg["id"])

    assert updated_keg["status"] == "dirty"
    assert Decimal(updated_keg["current_volume_liters"]) == Decimal("0.000")
    assert updated_keg["customer_id"] is None
    assert updated_keg["beer_presentation_id"] is None
    assert updated_keg["production_batch_id"] is None


def test_washing_returned_empty_keg_makes_it_available(client):
    result = create_delivered_kegs(client)

    keg = result["kegs"][0]

    return_response = client.post(
        "/keg-movements/return",
        json={
            "keg_id": keg["id"],
            "resulting_volume_liters": "0.000",
        },
    )
    assert return_response.status_code == 201

    washing_response = client.post(
        "/keg-movements/wash",
        json={
            "keg_id": keg["id"],
        },
    )

    assert washing_response.status_code == 201

    movement = washing_response.json()

    assert movement["movement_type"] == "washing"
    assert movement["previous_status"] == "dirty"
    assert movement["new_status"] == "clean_available"

    updated_keg = get_keg_by_id(client, keg["id"])

    assert updated_keg["status"] == "clean_available"
    assert Decimal(updated_keg["current_volume_liters"]) == Decimal("0.000")
    assert updated_keg["beer_presentation_id"] is None
    assert updated_keg["production_batch_id"] is None
    assert updated_keg["customer_id"] is None


def test_transferring_keg_remnants_recovers_bulk_beer(client):
    result = create_delivered_kegs(client, quantity=2)

    first_keg, second_keg = result["kegs"]

    for keg in (first_keg, second_keg):
        return_response = client.post(
            "/keg-movements/return",
            json={
                "keg_id": keg["id"],
                "resulting_volume_liters": "0.200",
            },
        )
        assert return_response.status_code == 201
        assert return_response.json()["new_status"] == "tapped"

    transfer_response = client.post(
        "/keg-movements/transfer-remnants",
        json={
            "source_keg_ids": [
                first_keg["id"],
                second_keg["id"],
            ],
            "notes": "Recovery test.",
        },
    )

    assert transfer_response.status_code == 201

    transfer = transfer_response.json()

    assert transfer["production_batch_id"] == result["data"]["production_batch"]["id"]
    assert Decimal(transfer["recovered_volume_liters"]) == Decimal("0.400")

    for keg in (first_keg, second_keg):
        updated_keg = get_keg_by_id(client, keg["id"])

        assert updated_keg["status"] == "dirty"
        assert Decimal(updated_keg["current_volume_liters"]) == Decimal("0.000")
        assert updated_keg["beer_presentation_id"] is None
        assert updated_keg["production_batch_id"] is None
        assert updated_keg["customer_id"] is None

        movements_response = client.get(f"/kegs/{keg['id']}/movements")
        assert movements_response.status_code == 200

        assert any(
            movement["movement_type"] == "remnant_transfer"
            for movement in movements_response.json()
        )

    production_batches_response = client.get("/production-batches/")
    assert production_batches_response.status_code == 200

    updated_batch = next(
        batch
        for batch in production_batches_response.json()
        if batch["id"] == result["data"]["production_batch"]["id"]
    )

    assert Decimal(updated_batch["available_bulk_volume_liters"]) == Decimal("99.400")


def test_cannot_transfer_remnants_from_different_production_batches(client):
    first_result = create_delivered_kegs(client)

    first_keg = first_result["kegs"][0]

    first_return_response = client.post(
        "/keg-movements/return",
        json={
            "keg_id": first_keg["id"],
            "resulting_volume_liters": "0.200",
        },
    )
    assert first_return_response.status_code == 201

    second_batch_response = client.post(
        "/production-batches/",
        json={
            "code": "PB-IPA-SECOND-LOT",
            "recipe_id": first_result["data"]["production_batch"]["recipe_id"],
            "planned_volume_liters": "100.000",
        },
    )
    assert second_batch_response.status_code == 201

    second_batch = second_batch_response.json()

    complete_second_batch_response = client.post(
        f"/production-batches/{second_batch['code']}/complete",
        json={
            "produced_volume_liters": "100.000",
        },
    )
    assert complete_second_batch_response.status_code == 200

    second_run_response = client.post(
        "/packaging-runs/",
        json={
            "production_batch_id": second_batch["id"],
            "beer_presentation_id": (first_result["data"]["beer_presentation"]["id"]),
            "packaged_quantity": 1,
        },
    )
    assert second_run_response.status_code == 201

    second_run = second_run_response.json()

    second_keg_response = client.post(
        "/kegs/",
        json={
            "code": "K20-SECOND-LOT-001",
            "packaging_format_id": (
                first_result["data"]["beer_presentation"]["packaging_format_id"]
            ),
            "form_factor": "slim",
        },
    )
    assert second_keg_response.status_code == 201

    second_keg = second_keg_response.json()

    second_fill_response = client.post(
        "/keg-movements/fill",
        json={
            "keg_id": second_keg["id"],
            "packaging_run_id": second_run["id"],
        },
    )
    assert second_fill_response.status_code == 201

    second_customer_response = client.post(
        "/customers/",
        json={
            "name": "Second Lot Customer",
        },
    )
    assert second_customer_response.status_code == 201

    second_customer = second_customer_response.json()

    second_sale_response = client.post(
        "/sales/",
        json={
            "customer_id": second_customer["id"],
        },
    )
    assert second_sale_response.status_code == 201

    second_sale = second_sale_response.json()

    second_sale_item_response = client.post(
        "/sale-items/",
        json={
            "sale_id": second_sale["id"],
            "beer_presentation_id": (first_result["data"]["beer_presentation"]["id"]),
            "quantity": 1,
        },
    )
    assert second_sale_item_response.status_code == 201

    second_sale_completion_response = client.post(
        f"/sales/{second_sale['code']}/complete",
        json={
            "keg_ids": [second_keg["id"]],
        },
    )
    assert second_sale_completion_response.status_code == 200

    second_return_response = client.post(
        "/keg-movements/return",
        json={
            "keg_id": second_keg["id"],
            "resulting_volume_liters": "0.200",
        },
    )
    assert second_return_response.status_code == 201

    transfer_response = client.post(
        "/keg-movements/transfer-remnants",
        json={
            "source_keg_ids": [
                first_keg["id"],
                second_keg["id"],
            ],
        },
    )

    assert transfer_response.status_code == 409
    assert transfer_response.json() == {
        "detail": (
            "All source kegs must belong to the same beer presentation "
            "and production batch."
        )
    }

    first_updated_keg = get_keg_by_id(client, first_keg["id"])
    second_updated_keg = get_keg_by_id(client, second_keg["id"])

    assert first_updated_keg["status"] == "tapped"
    assert second_updated_keg["status"] == "tapped"

    assert Decimal(first_updated_keg["current_volume_liters"]) == Decimal("0.200")
    assert Decimal(second_updated_keg["current_volume_liters"]) == Decimal("0.200")


def create_keg_repackaging_context(client):
    data = create_completed_batch_with_presentation(
        client,
        packaging_format_type="keg",
        capacity_liters="20.000",
    )

    target_format_response = client.post(
        "/packaging-formats/",
        json={
            "name": "Test Repackaging Bottle 500 ml",
            "capacity_liters": "0.500",
            "format_type": "bottle",
        },
    )
    assert target_format_response.status_code == 201

    target_format = target_format_response.json()

    target_presentation_response = client.post(
        "/beer-presentations/",
        json={
            "name": "IPA Repackaging Bottle 500 ml",
            "beer_id": data["beer_presentation"]["beer_id"],
            "packaging_format_id": target_format["id"],
        },
    )
    assert target_presentation_response.status_code == 201

    target_presentation = target_presentation_response.json()

    for packaging_material in data["packaging_materials"]:
        response = client.post(
            "/beer-presentation-packaging-materials/",
            json={
                "beer_presentation_id": target_presentation["id"],
                "raw_material_id": packaging_material["id"],
                "required_quantity": "1.000",
            },
        )
        assert response.status_code == 201

    packaging_run_response = client.post(
        "/packaging-runs/",
        json={
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 1,
        },
    )
    assert packaging_run_response.status_code == 201

    packaging_run = packaging_run_response.json()

    keg_response = client.post(
        "/kegs/",
        json={
            "code": "K20-REPACKAGING-001",
            "packaging_format_id": (data["beer_presentation"]["packaging_format_id"]),
            "form_factor": "flat",
        },
    )
    assert keg_response.status_code == 201

    keg = keg_response.json()

    fill_response = client.post(
        "/keg-movements/fill",
        json={
            "keg_id": keg["id"],
            "packaging_run_id": packaging_run["id"],
        },
    )
    assert fill_response.status_code == 201

    return {
        "data": data,
        "keg": keg,
        "target_presentation": target_presentation,
    }


def get_beer_presentation_by_id(
    client,
    beer_presentation_id: int,
):
    response = client.get("/beer-presentations/")
    assert response.status_code == 200

    return next(
        presentation
        for presentation in response.json()
        if presentation["id"] == beer_presentation_id
    )


def test_repackaging_keg_into_bottles_updates_stock_and_keg(
    client,
):
    context = create_keg_repackaging_context(client)

    raw_materials_before = {
        raw_material["id"]: Decimal(raw_material["current_stock"])
        for raw_material in client.get("/raw-materials/").json()
    }

    response = client.post(
        "/keg-repackaging-runs/",
        json={
            "keg_id": context["keg"]["id"],
            "target_beer_presentation_id": (context["target_presentation"]["id"]),
            "packaged_quantity": 36,
            "remaining_volume_liters": "1.500",
            "notes": "Bottling loss test.",
        },
    )

    assert response.status_code == 201

    repackaging_run = response.json()

    assert repackaging_run["code"] == "ENV2-000001"
    assert Decimal(repackaging_run["packaged_volume_liters"]) == Decimal("18.000")
    assert Decimal(repackaging_run["remaining_volume_liters"]) == Decimal("1.500")
    assert Decimal(repackaging_run["waste_volume_liters"]) == Decimal("0.500")

    source_presentation = get_beer_presentation_by_id(
        client,
        context["data"]["beer_presentation"]["id"],
    )
    target_presentation = get_beer_presentation_by_id(
        client,
        context["target_presentation"]["id"],
    )

    assert source_presentation["current_stock"] == 0
    assert target_presentation["current_stock"] == 36

    updated_keg = get_keg_by_id(
        client,
        context["keg"]["id"],
    )

    assert updated_keg["status"] == "tapped"
    assert Decimal(updated_keg["current_volume_liters"]) == Decimal("1.500")
    assert (
        updated_keg["beer_presentation_id"]
        == context["data"]["beer_presentation"]["id"]
    )

    raw_materials_after = {
        raw_material["id"]: Decimal(raw_material["current_stock"])
        for raw_material in client.get("/raw-materials/").json()
    }

    for packaging_material in context["data"]["packaging_materials"]:
        assert raw_materials_after[packaging_material["id"]] == raw_materials_before[
            packaging_material["id"]
        ] - Decimal("36.000")


def test_repackaging_cannot_exceed_keg_volume_and_is_atomic(
    client,
):
    context = create_keg_repackaging_context(client)

    response = client.post(
        "/keg-repackaging-runs/",
        json={
            "keg_id": context["keg"]["id"],
            "target_beer_presentation_id": (context["target_presentation"]["id"]),
            "packaged_quantity": 41,
            "remaining_volume_liters": "0.000",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "The produced bottles and remaining volume exceed the keg current volume."
        )
    }

    source_presentation = get_beer_presentation_by_id(
        client,
        context["data"]["beer_presentation"]["id"],
    )
    target_presentation = get_beer_presentation_by_id(
        client,
        context["target_presentation"]["id"],
    )
    updated_keg = get_keg_by_id(
        client,
        context["keg"]["id"],
    )

    assert source_presentation["current_stock"] == 1
    assert target_presentation["current_stock"] == 0
    assert updated_keg["status"] == "filled"
    assert Decimal(updated_keg["current_volume_liters"]) == Decimal("20.000")
    assert client.get("/keg-repackaging-runs/").json() == []


def test_primary_packaging_only_allows_keg_presentations(client):
    data = create_completed_batch_with_presentation(
        client,
        packaging_format_type="bottle",
    )

    response = client.post(
        "/packaging-runs/",
        json={
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "packaged_quantity": 1,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": ("Primary packaging runs can only use keg presentations.")
    }


def test_fill_keg_directly_from_bulk_creates_run_and_traceability(client):
    data = create_completed_batch_with_presentation(
        client,
        packaging_format_type="keg",
    )

    keg_response = client.post(
        "/kegs/",
        json={
            "code": "K20-DIRECT-001",
            "packaging_format_id": (data["beer_presentation"]["packaging_format_id"]),
            "form_factor": "flat",
        },
    )
    assert keg_response.status_code == 201

    keg = keg_response.json()

    response = client.post(
        "/keg-movements/fill-from-bulk",
        json={
            "keg_id": keg["id"],
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
        },
    )

    assert response.status_code == 201

    movement = response.json()

    assert movement["keg_id"] == keg["id"]
    assert movement["movement_type"] == "filling"
    assert movement["new_status"] == "filled"
    assert movement["production_batch_id"] == (data["production_batch"]["id"])
    assert movement["beer_presentation_id"] == (data["beer_presentation"]["id"])
    assert movement["packaging_run_id"] is not None

    packaging_runs = client.get("/packaging-runs/").json()

    assert len(packaging_runs) == 1
    assert packaging_runs[0]["id"] == movement["packaging_run_id"]
    assert packaging_runs[0]["packaged_quantity"] == 1

    production_batch = client.get("/production-batches/").json()[0]

    assert Decimal(production_batch["available_bulk_volume_liters"]) == Decimal(
        "99.500"
    )

    beer_presentation = client.get("/beer-presentations/").json()[0]

    assert beer_presentation["current_stock"] == 1

    updated_keg = client.get(f"/kegs/by-code/{keg['code']}").json()

    assert updated_keg["status"] == "filled"
    assert updated_keg["production_batch_id"] == (data["production_batch"]["id"])


def test_finished_product_stock_report_includes_filled_kegs(client):
    data = create_completed_batch_with_presentation(
        client,
        packaging_format_type="keg",
        capacity_liters="20.000",
    )

    keg_response = client.post(
        "/kegs/",
        json={
            "code": "K20-STOCK-001",
            "packaging_format_id": (data["beer_presentation"]["packaging_format_id"]),
            "form_factor": "flat",
        },
    )
    assert keg_response.status_code == 201

    filling_response = client.post(
        "/keg-movements/fill-from-bulk",
        json={
            "keg_id": keg_response.json()["id"],
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
        },
    )
    assert filling_response.status_code == 201

    response = client.get("/finished-product-stock/kegs")

    assert response.status_code == 200

    item = next(
        item
        for item in response.json()
        if item["beer_id"] == data["beer_presentation"]["beer_id"]
    )

    assert item["keg_count"] == 1
    assert item["form_factor"] == "flat"
    assert Decimal(item["total_volume_liters"]) == Decimal("20.000")


def test_finished_product_stock_report_includes_bottles(client):
    context = create_keg_repackaging_context(client)

    repackaging_response = client.post(
        "/keg-repackaging-runs/",
        json={
            "keg_id": context["keg"]["id"],
            "target_beer_presentation_id": (context["target_presentation"]["id"]),
            "packaged_quantity": 36,
            "remaining_volume_liters": "1.500",
        },
    )
    assert repackaging_response.status_code == 201

    response = client.get("/finished-product-stock/packaged")

    assert response.status_code == 200

    item = next(
        item
        for item in response.json()
        if item["beer_presentation_id"] == context["target_presentation"]["id"]
    )

    assert item["current_stock"] == 36
    assert Decimal(item["total_volume_liters"]) == Decimal("18.000")


def test_delivering_order_with_keg_updates_stock_and_keg_traceability(
    client,
):
    data = create_completed_batch_with_presentation(
        client,
        packaging_format_type="keg",
        capacity_liters="20.000",
    )

    keg_response = client.post(
        "/kegs/",
        json={
            "code": "K20-ORDER-001",
            "packaging_format_id": (data["beer_presentation"]["packaging_format_id"]),
            "form_factor": "flat",
        },
    )
    assert keg_response.status_code == 201

    keg = keg_response.json()

    filling_response = client.post(
        "/keg-movements/fill-from-bulk",
        json={
            "keg_id": keg["id"],
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
        },
    )
    assert filling_response.status_code == 201

    customer_response = client.post(
        "/customers/",
        json={
            "name": "Keg Order Customer",
        },
    )
    assert customer_response.status_code == 201

    customer = customer_response.json()

    order_response = client.post(
        "/delivery-orders/",
        json={
            "customer_id": customer["id"],
        },
    )
    assert order_response.status_code == 201

    order = order_response.json()

    item_response = client.post(
        f"/delivery-orders/{order['code']}/items",
        json={
            "beer_presentation_id": data["beer_presentation"]["id"],
            "requested_quantity": 1,
        },
    )
    assert item_response.status_code == 201

    item = item_response.json()

    assert (
        client.post(
            f"/delivery-orders/{order['code']}/start-picking",
        ).status_code
        == 200
    )

    assert (
        client.patch(
            f"/delivery-orders/{order['code']}/items/{item['id']}/picking",
            json={"picked_quantity": 1},
        ).status_code
        == 200
    )

    assignment_response = client.post(
        f"/delivery-orders/{order['code']}/kegs",
        json={
            "keg_id": keg["id"],
        },
    )
    assert assignment_response.status_code == 201

    delivery_response = client.post(
        f"/delivery-orders/{order['code']}/deliver",
        json={},
    )
    assert delivery_response.status_code == 200

    delivered_order = delivery_response.json()

    assert delivered_order["status"] == "delivered_pending_pricing"
    assert delivered_order["delivery_note_code"] == "REM-000001"

    updated_keg = client.get(
        f"/kegs/by-code/{keg['code']}",
    ).json()

    assert updated_keg["status"] == "at_customer"
    assert updated_keg["customer_id"] == customer["id"]

    presentation = get_beer_presentation_by_id(
        client,
        data["beer_presentation"]["id"],
    )

    assert presentation["current_stock"] == 0

    keg_movements = client.get(
        f"/kegs/{keg['id']}/movements",
    ).json()

    assert keg_movements[0]["movement_type"] == "delivery"
    assert keg_movements[0]["delivery_order_id"] == order["id"]
    assert keg_movements[0]["reference"] == delivered_order["delivery_note_code"]

def test_fill_last_keg_from_bulk_with_partial_volume(
    client,
):
    data = create_completed_batch_with_presentation(
        client,
        packaging_format_type="keg",
        capacity_liters="20.000",
    )

    keg_response = client.post(
        "/kegs/",
        json={
            "code": "K20-PARTIAL-001",
            "packaging_format_id": (
                data["beer_presentation"]["packaging_format_id"]
            ),
            "form_factor": "flat",
        },
    )
    assert keg_response.status_code == 201

    keg = keg_response.json()

    response = client.post(
        "/keg-movements/fill-from-bulk",
        json={
            "keg_id": keg["id"],
            "production_batch_id": data["production_batch"]["id"],
            "beer_presentation_id": data["beer_presentation"]["id"],
            "filled_volume_liters": "8.500",
        },
    )

    assert response.status_code == 201

    movement = response.json()
    assert Decimal(movement["resulting_volume_liters"]) == Decimal("8.500")

    packaging_runs = client.get("/packaging-runs/").json()
    assert len(packaging_runs) == 1
    assert Decimal(packaging_runs[0]["packaged_volume_liters"]) == Decimal(
        "8.500"
    )

    production_batch = client.get("/production-batches/").json()[0]
    assert Decimal(
        production_batch["available_bulk_volume_liters"]
    ) == Decimal("91.500")

    updated_keg = client.get(
        f"/kegs/by-code/{keg['code']}",
    ).json()
    assert Decimal(updated_keg["current_volume_liters"]) == Decimal(
        "8.500"
    )