from decimal import Decimal


def create_cost_estimate_data(client):
    category = client.post(
        "/categories/",
        json={"name": "Cost category"},
    ).json()

    unit = client.post(
        "/units/",
        json={
            "name": "Cost unit",
            "symbol": "u",
        },
    ).json()

    def create_raw_material(
        code: str,
        name: str,
        current_cost: str,
    ):
        response = client.post(
            "/raw-materials/",
            json={
                
                "name": name,
                "category_id": category["id"],
                "unit_id": unit["id"],
                "minimum_stock": "0.000",
                "current_cost": current_cost,
            },
        )

        assert response.status_code == 201
        return response.json()

    malt = create_raw_material(
        "COST-MALT",
        "Cost Malt",
        "2.00",
    )
    bottle = create_raw_material(
        "COST-BOTTLE",
        "Cost Bottle",
        "1.00",
    )
    cap = create_raw_material(
        "COST-CAP",
        "Cost Cap",
        "0.50",
    )
    label = create_raw_material(
        "COST-LABEL",
        "Cost Label",
        "0.25",
    )

    beer = client.post(
        "/beers/",
        json={
            
            "name": "Cost Beer",
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

    ingredient_response = client.post(
        "/recipe-ingredients/",
        json={
            "recipe_id": recipe["id"],
            "raw_material_id": malt["id"],
            "required_quantity": "10.000",
        },
    )
    assert ingredient_response.status_code == 201

    packaging_format = client.post(
        "/packaging-formats/",
        json={
            
            "name": "Cost Bottle 500 ml",
            "capacity_liters": "0.500",
        },
    ).json()

    beer_presentation = client.post(
        "/beer-presentations/",
        json={
            
            "name": "Cost Presentation",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
        },
    ).json()

    for raw_material in (bottle, cap, label):
        response = client.post(
            "/beer-presentation-packaging-materials/",
            json={
                "beer_presentation_id": beer_presentation["id"],
                "raw_material_id": raw_material["id"],
                "required_quantity": "1.000",
            },
        )
        assert response.status_code == 201

    return {
        "beer": beer,
        "recipe": recipe,
        "beer_presentation": beer_presentation,
    }


def test_get_beer_presentation_cost_estimate(client):
    data = create_cost_estimate_data(client)

    response = client.get(
        f"/beer-presentations/"
        f"{data['beer_presentation']['id']}/cost-estimate",
        params={"recipe_id": data["recipe"]["id"]},
    )

    assert response.status_code == 200

    estimate = response.json()

    # 10 unidades / 100 L × 0,5 L × $2,00 = $0,10
    assert Decimal(estimate["beer_cost"]) == Decimal("0.10")

    # Botella $1,00 + tapa $0,50 + etiqueta $0,25
    assert Decimal(estimate["packaging_material_cost"]) == Decimal("1.75")
    assert Decimal(estimate["total_unit_cost"]) == Decimal("1.85")

    assert len(estimate["components"]) == 4


def test_cost_estimate_rejects_recipe_from_another_beer(client):
    data = create_cost_estimate_data(client)

    other_beer = client.post(
        "/beers/",
        json={
            
            "name": "Other Cost Beer",
        },
    ).json()

    other_recipe = client.post(
        "/recipes/",
        json={
            "beer_id": other_beer["id"],
            "version": 1,
            "target_volume_liters": "100.000",
        },
    ).json()

    response = client.get(
        f"/beer-presentations/"
        f"{data['beer_presentation']['id']}/cost-estimate",
        params={"recipe_id": other_recipe["id"]},
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "The recipe does not belong to the beer presentation beer."
        )
    }