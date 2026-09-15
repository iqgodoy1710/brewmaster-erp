import app.api.auth_dependencies as auth_dependencies
from app.models.enums import UserRole
from app.schemas.user import UserCreate
from app.services.user_service import UserService

TEST_PASSWORD = "secure-password-123"


def create_test_user(
    db,
    username: str,
    role: UserRole,
):
    return UserService.create(
        db,
        UserCreate(
            username=username,
            full_name="Test User",
            password=TEST_PASSWORD,
            role=role,
        ),
    )


def get_auth_headers(
    client,
    username: str,
) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    return {
        "Authorization": (
            f"Bearer {response.json()['access_token']}"
        )
    }


def test_login_returns_token_and_current_user_without_password_hash(
    client,
    db,
):
    user = create_test_user(
        db,
        "admin_test",
        UserRole.ADMIN,
    )

    headers = get_auth_headers(client, user.username)

    response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["username"] == user.username
    assert response.json()["role"] == "admin"
    assert "password_hash" not in response.json()


def test_user_management_requires_an_administrator(
    client,
    db,
):
    admin = create_test_user(
        db,
        "admin_test",
        UserRole.ADMIN,
    )
    management = create_test_user(
        db,
        "management_test",
        UserRole.MANAGEMENT,
    )

    management_headers = get_auth_headers(
        client,
        management.username,
    )
    admin_headers = get_auth_headers(client, admin.username)

    response = client.get(
        "/users/",
        headers=management_headers,
    )
    assert response.status_code == 403

    response = client.post(
        "/users/",
        headers=admin_headers,
        json={
            "username": "operator_test",
            "full_name": "Operator User",
            "password": TEST_PASSWORD,
            "role": "operator",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "operator"
    assert "password_hash" not in response.json()


def test_sales_require_management_or_administrator_when_auth_is_enabled(
    client,
    db,
    monkeypatch,
):
    management = create_test_user(
        db,
        "management_test",
        UserRole.MANAGEMENT,
    )
    operator = create_test_user(
        db,
        "operator_test",
        UserRole.OPERATOR,
    )

    monkeypatch.setattr(
        auth_dependencies,
        "AUTH_REQUIRED",
        True,
    )

    management_headers = get_auth_headers(
        client,
        management.username,
    )
    operator_headers = get_auth_headers(
        client,
        operator.username,
    )

    assert client.get("/sales/").status_code == 401
    assert (
        client.get(
            "/sales/",
            headers=management_headers,
        ).status_code
        == 200
    )
    assert (
        client.get(
            "/sales/",
            headers=operator_headers,
        ).status_code
        == 403
    )

def test_administrator_can_deactivate_another_user_but_not_self(
    client,
    db,
):
    admin = create_test_user(
        db,
        "admin_test",
        UserRole.ADMIN,
    )
    operator = create_test_user(
        db,
        "operator_test",
        UserRole.OPERATOR,
    )

    admin_headers = get_auth_headers(
        client,
        admin.username,
    )

    response = client.patch(
        f"/users/{operator.id}",
        headers=admin_headers,
        json={"active": False},
    )

    assert response.status_code == 200
    assert response.json()["active"] is False

    response = client.patch(
        f"/users/{admin.id}",
        headers=admin_headers,
        json={"active": False},
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "You cannot deactivate your own account."
    }

def test_operator_can_read_operational_catalogs_but_cannot_modify_them(
    client,
    db,
    monkeypatch,
):
    operator = create_test_user(
        db,
        "operator_catalog_test",
        UserRole.OPERATOR,
    )

    monkeypatch.setattr(
        auth_dependencies,
        "AUTH_REQUIRED",
        True,
    )

    headers = get_auth_headers(client, operator.username)

    readable_paths = [
        "/beers/",
        "/packaging-formats/",
        "/beer-presentations/",
        "/recipes/",
        "/categories/",
        "/units/",
        "/customers/",
        "/suppliers/",
        "/raw-materials/",
    ]

    for path in readable_paths:
        response = client.get(path, headers=headers)
        assert response.status_code == 200, path

    protected_creations = [
        ("/beers/", {"name": "Forbidden Beer"}),
        (
            "/packaging-formats/",
            {
                "name": "Forbidden Format",
                "capacity_liters": "1.000",
                "format_type": "other",
            },
        ),
        ("/categories/", {"name": "Forbidden Category"}),
        (
            "/units/",
            {
                "name": "Forbidden Unit",
                "symbol": "fu",
            },
        ),
        ("/customers/", {"name": "Forbidden Customer"}),
        (
            "/suppliers/",
            {
                "name": "Forbidden Supplier",
                "tax_id": "FORBIDDEN-001",
            },
        ),
    ]

    for path, payload in protected_creations:
        response = client.post(
            path,
            headers=headers,
            json=payload,
        )
        assert response.status_code == 403, path


def test_only_administrator_can_register_kegs(
    client,
    db,
    monkeypatch,
):
    packaging_format = client.post(
        "/packaging-formats/",
        json={
            "name": "Authorization Keg 20 L",
            "capacity_liters": "20.000",
            "format_type": "keg",
        },
    ).json()

    admin = create_test_user(
        db,
        "admin_keg_test",
        UserRole.ADMIN,
    )
    management = create_test_user(
        db,
        "management_keg_test",
        UserRole.MANAGEMENT,
    )
    operator = create_test_user(
        db,
        "operator_keg_test",
        UserRole.OPERATOR,
    )

    monkeypatch.setattr(
        auth_dependencies,
        "AUTH_REQUIRED",
        True,
    )

    payload = {
        "code": "AUTH-KEG-001",
        "packaging_format_id": packaging_format["id"],
        "form_factor": "standard",
    }

    management_response = client.post(
        "/kegs/",
        headers=get_auth_headers(client, management.username),
        json=payload,
    )
    operator_response = client.post(
        "/kegs/",
        headers=get_auth_headers(client, operator.username),
        json=payload,
    )
    admin_response = client.post(
        "/kegs/",
        headers=get_auth_headers(client, admin.username),
        json=payload,
    )

    assert management_response.status_code == 403
    assert operator_response.status_code == 403
    assert admin_response.status_code == 201

def test_all_roles_can_register_raw_material_movements(
    client,
    db,
    monkeypatch,
):
    category = client.post(
        "/categories/",
        json={"name": "Authorization Category"},
    ).json()

    unit = client.post(
        "/units/",
        json={
            "name": "Authorization Unit",
            "symbol": "au",
        },
    ).json()

    raw_material = client.post(
        "/raw-materials/",
        json={
            "name": "Authorization Material",
            "category_id": category["id"],
            "unit_id": unit["id"],
            "minimum_stock": "0",
            "current_cost": "0",
        },
    ).json()

    users = [
        create_test_user(db, "admin_movement_test", UserRole.ADMIN),
        create_test_user(
            db,
            "management_movement_test",
            UserRole.MANAGEMENT,
        ),
        create_test_user(
            db,
            "operator_movement_test",
            UserRole.OPERATOR,
        ),
    ]

    monkeypatch.setattr(
        auth_dependencies,
        "AUTH_REQUIRED",
        True,
    )

    for user in users:
        response = client.post(
            "/raw-material-stock-movements/",
            headers=get_auth_headers(client, user.username),
            json={
                "raw_material_id": raw_material["id"],
                "movement_type": "inventory_adjustment_in",
                "quantity": "1.000",
            },
        )

        assert response.status_code == 201, user.role