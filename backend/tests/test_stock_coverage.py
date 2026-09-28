def create_category_and_unit(client):
    category_response = client.post(
        "/categories/",
        json={"name": "Cobertura de stock"},
    )
    assert category_response.status_code in (200, 201)

    unit_response = client.post(
        "/units/",
        json={
            "name": "Unidad de cobertura",
            "symbol": "u",
        },
    )
    assert unit_response.status_code in (200, 201)

    return (
        category_response.json(),
        unit_response.json(),
    )


def create_raw_material(
    client,
    name: str,
    category_id: int,
    unit_id: int,
    minimum_stock: str = "0.000",
):
    response = client.post(
        "/raw-materials/",
        json={
            "name": name,
            "category_id": category_id,
            "unit_id": unit_id,
            "minimum_stock": minimum_stock,
            "current_cost": "0.00",
        },
    )

    assert response.status_code == 201
    return response.json()


def add_raw_material_stock(
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
            "reference": "COVERAGE-TEST",
        },
    )

    assert response.status_code == 201


def add_presentation_stock(
    client,
    beer_presentation_id: int,
    quantity: int,
):
    response = client.post(
        "/beer-presentation-stock-movements/",
        json={
            "beer_presentation_id": beer_presentation_id,
            "movement_type": "initial_balance",
            "quantity": quantity,
            "reference": "COVERAGE-TEST",
        },
    )

    assert response.status_code == 201


def test_stock_coverage_calculates_production_and_packaging_requirements(
    client,
):
    category, unit = create_category_and_unit(client)

    malt = create_raw_material(
        client,
        "Malta cobertura",
        category["id"],
        unit["id"],
        minimum_stock="5.000",
    )
    bottle = create_raw_material(
        client,
        "Botella cobertura",
        category["id"],
        unit["id"],
        minimum_stock="10.000",
    )

    add_raw_material_stock(
        client,
        malt["id"],
        "50.000",
    )
    add_raw_material_stock(
        client,
        bottle["id"],
        "20.000",
    )

    beer_response = client.post(
        "/beers/",
        json={
            "name": "IPA cobertura",
            "minimum_stock_liters": "800.000",
        },
    )
    assert beer_response.status_code == 201
    beer = beer_response.json()

    recipe_response = client.post(
        "/recipes/",
        json={
            "beer_id": beer["id"],
            "version": 1,
            "target_volume_liters": "100.000",
            "is_current": True,
        },
    )
    assert recipe_response.status_code == 201
    recipe = recipe_response.json()

    ingredient_response = client.post(
        "/recipe-ingredients/",
        json={
            "recipe_id": recipe["id"],
            "raw_material_id": malt["id"],
            "required_quantity": "10.000",
        },
    )
    assert ingredient_response.status_code == 201

    format_response = client.post(
        "/packaging-formats/",
        json={
            "name": "Botella cobertura 1 L",
            "capacity_liters": "1.000",
            "format_type": "bottle",
        },
    )
    assert format_response.status_code == 201
    packaging_format = format_response.json()

    presentation_response = client.post(
        "/beer-presentations/",
        json={
            "name": "IPA cobertura botella 1 L",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
            "minimum_stock": 100,
        },
    )
    assert presentation_response.status_code == 201
    presentation = presentation_response.json()

    material_response = client.post(
        "/beer-presentation-packaging-materials/",
        json={
            "beer_presentation_id": presentation["id"],
            "raw_material_id": bottle["id"],
            "required_quantity": "1.000",
        },
    )
    assert material_response.status_code == 201

    add_presentation_stock(
        client,
        presentation["id"],
        40,
    )

    response = client.get(
        "/finished-product-stock/raw-material-requirements"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["warnings"] == []

    requirements = {
        requirement["raw_material_id"]: requirement
        for requirement in data["requirements"]
    }

    malt_requirement = requirements[malt["id"]]

    # Hay 40 litros en botellas. Para cubrir el mínimo general
    # de 800 litros todavía deben producirse 760 litros.
    # La receta utiliza 10 unidades cada 100 litros:
    # 760 / 100 * 10 = 76.
    assert (
        malt_requirement["production_required_quantity"]
        == "76.000"
    )
    assert (
        malt_requirement["packaging_required_quantity"]
        == "0.000"
    )
    assert (
        malt_requirement["total_required_quantity"]
        == "76.000"
    )
    assert malt_requirement["current_stock"] == "50.000"
    assert malt_requirement["minimum_stock"] == "5.000"
    assert malt_requirement["projected_stock"] == "-26.000"
    assert malt_requirement["shortage_quantity"] == "31.000"
    assert malt_requirement["has_shortage"] is True

    bottle_requirement = requirements[bottle["id"]]

    # La presentación requiere 100 botellas y existen 40.
    # Se necesitan 60 envases, sin agregar otros 60 litros
    # al requerimiento de producción de cerveza.
    assert (
        bottle_requirement["production_required_quantity"]
        == "0.000"
    )
    assert (
        bottle_requirement["packaging_required_quantity"]
        == "60.000"
    )
    assert (
        bottle_requirement["total_required_quantity"]
        == "60.000"
    )
    assert bottle_requirement["current_stock"] == "20.000"
    assert bottle_requirement["minimum_stock"] == "10.000"
    assert bottle_requirement["projected_stock"] == "-40.000"
    assert bottle_requirement["shortage_quantity"] == "50.000"
    assert bottle_requirement["has_shortage"] is True


def test_stock_coverage_warns_when_beer_has_no_current_recipe(
    client,
):
    beer_response = client.post(
        "/beers/",
        json={
            "name": "Cerveza sin receta",
            "minimum_stock_liters": "100.000",
        },
    )
    assert beer_response.status_code == 201
    beer = beer_response.json()

    response = client.get(
        "/finished-product-stock/raw-material-requirements"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["requirements"] == []
    assert len(data["warnings"]) == 1

    warning = data["warnings"][0]

    assert warning["source_type"] == "beer"
    assert warning["source_code"] == beer["code"]
    assert warning["source_name"] == beer["name"]
    assert (
        warning["detail"]
        == (
            "La cerveza tiene faltante de cobertura "
            "pero no posee una receta vigente."
        )
    )