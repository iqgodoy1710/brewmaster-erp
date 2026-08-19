import jwt
from app.common.exceptions import (
    InsufficientPermissionsError,
    InvalidCredentialsError,
)
from app.core.config import AUTH_REQUIRED
from app.core.security import decode_access_token
from app.crud.user import get_user_by_id
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.models.user import User
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_current_user(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> User:
    if credentials is None:
        raise InvalidCredentialsError("Authentication is required.")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (
        jwt.InvalidTokenError,
        KeyError,
        TypeError,
        ValueError,
    ):
        raise InvalidCredentialsError("Invalid or expired access token.")

    user = get_user_by_id(db, user_id)

    if not user or not user.active:
        raise InvalidCredentialsError("Invalid or expired access token.")

    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    return _resolve_current_user(credentials, db)


def get_current_user_if_auth_required(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User | None:
    if not AUTH_REQUIRED:
        return None

    return _resolve_current_user(credentials, db)


def require_roles(*allowed_roles: UserRole):
    def role_dependency(
        current_user: User | None = Depends(
            get_current_user_if_auth_required
        ),
    ) -> User | None:
        if not AUTH_REQUIRED:
            return current_user

        if current_user is None or current_user.role not in allowed_roles:
            raise InsufficientPermissionsError(
                "You do not have permission to perform this action."
            )

        return current_user

    return role_dependency

def require_authenticated_roles(*allowed_roles: UserRole):
    def role_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise InsufficientPermissionsError(
                "You do not have permission to perform this action."
            )

        return current_user

    return role_dependency