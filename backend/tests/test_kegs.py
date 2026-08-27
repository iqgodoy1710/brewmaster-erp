def create_test_keg_format(client):
    response = client.post(
        "/packaging-formats/",
        json={
            
            "name": "Test Keg 20 L",
            "capacity_liters": "20.000",
            "format_type": "keg",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_keg(client):
    packaging_format = create_test_keg_format(client)

    response = client.post(
        "/kegs/",
        json={
            "code": "K20-F-001",
            "packaging_format_id": packaging_format["id"],
            "form_factor": "flat",
            "notes": "Flat test keg.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["code"] == "K20-F-001"
    assert data["packaging_format_id"] == packaging_format["id"]
    assert data["form_factor"] == "flat"
    assert data["status"] == "clean_available"
    assert data["current_volume_liters"] == "0.000"
    assert data["beer_presentation_id"] is None
    assert data["production_batch_id"] is None
    assert data["customer_id"] is None


def test_cannot_create_keg_with_non_keg_format(client):
    response = client.post(
        "/packaging-formats/",
        json={
            
            "name": "Test Bottle 500 ml",
            "capacity_liters": "0.500",
            "format_type": "bottle",
        },
    )

    assert response.status_code == 201

    packaging_format = response.json()

    response = client.post(
        "/kegs/",
        json={
            "code": "K20-F-001",
            "packaging_format_id": packaging_format["id"],
            "form_factor": "flat",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "A keg must use a packaging format of type keg."
        )
    }


def test_cannot_create_kegs_with_duplicate_codes(client):
    packaging_format = create_test_keg_format(client)

    first_response = client.post(
        "/kegs/",
        json={
            "code": "K20-F-001",
            "packaging_format_id": packaging_format["id"],
        },
    )
    second_response = client.post(
        "/kegs/",
        json={
            "code": "k20-f-001",
            "packaging_format_id": packaging_format["id"],
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "A keg with this code already exists."
    }


def test_get_kegs_returns_active_kegs(client):
    packaging_format = create_test_keg_format(client)

    for code, form_factor in (
        ("K20-F-001", "flat"),
        ("K20-S-001", "slim"),
    ):
        response = client.post(
            "/kegs/",
            json={
                "code": code,
                "packaging_format_id": packaging_format["id"],
                "form_factor": form_factor,
            },
        )

        assert response.status_code == 201

    response = client.get("/kegs/")

    assert response.status_code == 200
    assert {keg["code"] for keg in response.json()} == {
        "K20-F-001",
        "K20-S-001",
    }

def test_get_keg_by_code_returns_active_keg(client):
    packaging_format = create_test_keg_format(client)

    create_response = client.post(
        "/kegs/",
        json={
            "code": "K20-F-001",
            "packaging_format_id": packaging_format["id"],
            "form_factor": "flat",
        },
    )

    assert create_response.status_code == 201

    keg = create_response.json()

    response = client.get(
        f"/kegs/by-code/{keg['code'].lower()}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == keg["id"]
    assert response.json()["code"] == keg["code"]