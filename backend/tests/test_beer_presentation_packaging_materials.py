from decimal import Decimal


def create_beer_presentation_and_raw_material(client):
    category = client.post(
        "/categories/",
        json={"name": "Packaging"},
    ).json()

    unit = client.post(
        "/units/",
        json={
            "name": "Unit",
            "symbol": "u",
        },
    ).json()

    raw_material = client.post(
        "/raw-materials/",
        json={
            "name": "500 ml Bottle",
            "category_id": category["id"],
            "unit_id": unit["id"],
            "minimum_stock": "0.000",
            "current_cost": "0.000",
        },
    ).json()

    beer = client.post(
        "/beers/",
        json={
            "name": "India Pale Ale",
        },
    ).json()

    packaging_format = client.post(
        "/packaging-formats/",
        json={
            "name": "Bottle 500 ml",
            "capacity_liters": "0.500",
        },
    ).json()

    beer_presentation = client.post(
        "/beer-presentations/",
        json={
            "name": "IPA Bottle 500 ml",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
        },
    ).json()

    return beer_presentation, raw_material


def test_create_beer_presentation_packaging_material(client):
    beer_presentation, raw_material = create_beer_presentation_and_raw_material(client)

    response = client.post(
        "/beer-presentation-packaging-materials/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "raw_material_id": raw_material["id"],
            "required_quantity": "1.000",
        },
    )

    assert response.status_code == 201

    created_packaging_material = response.json()

    assert created_packaging_material["beer_presentation_id"] == beer_presentation["id"]
    assert created_packaging_material["raw_material_id"] == raw_material["id"]
    assert Decimal(created_packaging_material["required_quantity"]) == Decimal("1.000")


def test_cannot_add_duplicate_packaging_material_to_presentation(client):
    beer_presentation, raw_material = create_beer_presentation_and_raw_material(client)

    payload = {
        "beer_presentation_id": beer_presentation["id"],
        "raw_material_id": raw_material["id"],
        "required_quantity": "1.000",
    }

    first_response = client.post(
        "/beer-presentation-packaging-materials/",
        json=payload,
    )
    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/beer-presentation-packaging-materials/",
        json=payload,
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": (
            "This raw material is already a packaging material "
            "of the beer presentation."
        )
    }


def test_get_packaging_materials_by_beer_presentation(client):
    beer_presentation, raw_material = create_beer_presentation_and_raw_material(client)

    creation_response = client.post(
        "/beer-presentation-packaging-materials/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "raw_material_id": raw_material["id"],
            "required_quantity": "1.000",
        },
    )
    assert creation_response.status_code == 201

    response = client.get(
        f"/beer-presentations/{beer_presentation['id']}/packaging-materials"
    )

    assert response.status_code == 200

    packaging_materials = response.json()

    assert len(packaging_materials) == 1
    assert packaging_materials[0]["raw_material_id"] == raw_material["id"]
    assert Decimal(packaging_materials[0]["required_quantity"]) == Decimal("1.000")


def test_get_packaging_materials_for_nonexistent_presentation(client):
    response = client.get("/beer-presentations/999999/packaging-materials")

    assert response.status_code == 404
    assert response.json() == {"detail": "The beer presentation does not exist."}


def test_cannot_add_packaging_material_to_keg_presentation(client):
    beer_presentation, raw_material = create_beer_presentation_and_raw_material(client)

    keg_format_response = client.post(
        "/packaging-formats/",
        json={
            "name": "Test Keg 20 L",
            "capacity_liters": "20.000",
            "format_type": "keg",
        },
    )
    assert keg_format_response.status_code == 201

    keg_presentation_response = client.post(
        "/beer-presentations/",
        json={
            "name": "IPA Keg 20 L",
            "beer_id": beer_presentation["beer_id"],
            "packaging_format_id": keg_format_response.json()["id"],
        },
    )
    assert keg_presentation_response.status_code == 201

    response = client.post(
        "/beer-presentation-packaging-materials/",
        json={
            "beer_presentation_id": keg_presentation_response.json()["id"],
            "raw_material_id": raw_material["id"],
            "required_quantity": "1.000",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "Keg presentations do not use packaging materials because "
            "physical kegs are reusable."
        )
    }
