def test_create_supplier(client):
    response = client.post(
        "/suppliers/",
        json={
            "name": "Malt Supply Co.",
            "tax_id": "ESB12345678",
            "email": "sales@maltsupply.example",
            "phone": "+34 600 000 000",
            "address": "Madrid, Spain",
            "notes": "Main malt supplier.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Malt Supply Co."
    assert data["tax_id"] == "ESB12345678"
    assert data["active"] is True


def test_create_multiple_suppliers_without_tax_id(client):
    first_response = client.post(
        "/suppliers/",
        json={
            "name": "Hop Supplier",
        },
    )
    second_response = client.post(
        "/suppliers/",
        json={
            "name": "Yeast Supplier",
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert first_response.json()["tax_id"] is None
    assert second_response.json()["tax_id"] is None

def test_create_supplier_with_duplicate_tax_id_returns_conflict(
    client,
):
    first_supplier = {
        "name": "Malt Supply Co.",
        "tax_id": "ESB12345678",
    }
    second_supplier = {
        "name": "Another Supplier",
        "tax_id": "ESB12345678",
    }

    client.post("/suppliers/", json=first_supplier)

    response = client.post("/suppliers/", json=second_supplier)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A supplier with this tax ID already exists."
    }