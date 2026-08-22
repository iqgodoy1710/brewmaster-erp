def test_register_customer_payment_updates_account(client):
    customer_response = client.post(
        "/customers/",
        json={
            
            "name": "Payment Test Customer",
        },
    )
    assert customer_response.status_code == 201

    customer = customer_response.json()

    payment_response = client.post(
        "/customer-payments/",
        json={
            "customer_id": customer["id"],
            "amount": "100.00",
            "payment_method": "bank_transfer",
            "reference": "TRANSFER-TEST-001",
            "notes": "Payment test.",
        },
    )

    assert payment_response.status_code == 201

    payment = payment_response.json()

    assert payment["code"] == "PAG-000001"
    assert payment["amount"] == "100.00"
    assert payment["payment_method"] == "bank_transfer"

    account_response = client.get(
        f"/customers/{customer['id']}/account"
    )

    assert account_response.status_code == 200

    account = account_response.json()

    assert account["balance"] == "-100.00"
    assert len(account["movements"]) == 1

    movement = account["movements"][0]

    assert movement["movement_type"] == "payment"
    assert movement["amount"] == "100.00"
    assert movement["payment_id"] == payment["id"]
    assert movement["payment_code"] == payment["code"]