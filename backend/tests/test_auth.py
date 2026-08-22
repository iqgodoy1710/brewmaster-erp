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