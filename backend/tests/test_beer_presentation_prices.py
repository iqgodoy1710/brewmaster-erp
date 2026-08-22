def create_test_beer_presentation(
    client,
    suffix: str,
    minimum_stock: int = 0,
):
    beer_response = client.post(
        "/beers/",
        json={
            
            "name": f"Beer Alert {suffix}",
        },
    )
    assert beer_response.status_code == 201

    beer = beer_response.json()

    packaging_format_response = client.post(
        "/packaging-formats/",
        json={
            
            "name": f"Format Alert {suffix}",
            "capacity_liters": "0.500",
        },
    )
    assert packaging_format_response.status_code == 201

    packaging_format = packaging_format_response.json()

    presentation_response = client.post(
        "/beer-presentations/",
        json={
            
            "name": f"Presentation Alert {suffix}",
            "beer_id": beer["id"],
            "packaging_format_id": packaging_format["id"],
            "minimum_stock": minimum_stock,
        },
    )
    assert presentation_response.status_code == 201

    return presentation_response.json()

def test_creating_a_new_price_deactivates_the_previous_one(client):
    beer_presentation = create_test_beer_presentation(client, "PRICE")

    first_response = client.post(
        "/beer-presentation-prices/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "unit_price": "10.00",
            "notes": "Initial price.",
        },
    )

    assert first_response.status_code == 201
    assert first_response.json()["active"] is True

    second_response = client.post(
        "/beer-presentation-prices/",
        json={
            "beer_presentation_id": beer_presentation["id"],
            "unit_price": "12.50",
            "notes": "Updated price.",
        },
    )

    assert second_response.status_code == 201
    assert second_response.json()["active"] is True

    prices_response = client.get(
        f"/beer-presentations/{beer_presentation['id']}/prices"
    )

    assert prices_response.status_code == 200

    prices = prices_response.json()

    assert len(prices) == 2
    assert prices[0]["unit_price"] == "12.50"
    assert prices[0]["active"] is True
    assert prices[1]["unit_price"] == "10.00"
    assert prices[1]["active"] is False