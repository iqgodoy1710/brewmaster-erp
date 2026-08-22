def test_create_and_get_customers(client):
    creation_response = client.post(
        "/customers/",
        json={
            "name": "Example Brewery Customer",
            "tax_id": "B12345678",
            "email": "purchases@example.test",
        },
    )

    assert creation_response.status_code == 201

    created_customer = creation_response.json()

    assert created_customer["code"] == "CLI-000001"
    assert created_customer["name"] == "Example Brewery Customer"
    assert created_customer["tax_id"] == "B12345678"
    assert created_customer["active"] is True

    list_response = client.get("/customers/")

    assert list_response.status_code == 200
    assert list_response.json() == [created_customer]


def test_customers_receive_sequential_generated_codes(client):
    first_response = client.post(
        "/customers/",
        json={
            "name": "First Customer",
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/customers/",
        json={
            "name": "Second Customer",
        },
    )
    assert second_response.status_code == 201

    assert first_response.json()["code"] == "CLI-000001"
    assert second_response.json()["code"] == "CLI-000002"


def test_cannot_create_customer_with_duplicate_tax_id(client):
    first_response = client.post(
        "/customers/",
        json={
            "name": "First Customer",
            "tax_id": "B12345678",
        },
    )
    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/customers/",
        json={
            "name": "Second Customer",
            "tax_id": "B12345678",
        },
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": "A customer with this tax ID already exists."
    }


def test_can_create_multiple_customers_without_tax_id(client):
    first_response = client.post(
        "/customers/",
        json={
            "name": "First Customer",
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/customers/",
        json={
            "name": "Second Customer",
        },
    )
    assert second_response.status_code == 201

    customers = client.get("/customers/").json()

    assert len(customers) == 2
    assert customers[0]["code"] == "CLI-000001"
    assert customers[1]["code"] == "CLI-000002"
    assert customers[0]["tax_id"] is None
    assert customers[1]["tax_id"] is None