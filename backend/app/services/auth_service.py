from app.common.exceptions import InvalidCredentialsError
from app.core.security import create_access_token, verify_password
from app.crud.user import get_user_by_username
from app.schemas.auth import LoginRequest, TokenResponse
from sqlalchemy.orm import Session


class AuthService:
    @staticmethod
    def login(
        db: Session,
        login_data: LoginRequest,
    ) -> TokenResponse:
        user = get_user_by_username(
            db,
            login_data.username.strip().lower(),
        )

        if (
            not user
            or not user.active
            or not verify_password(
                login_data.password,
                user.password_hash,
            )
        ):
            raise InvalidCredentialsError(
                "Invalid username or password."
            )

        return TokenResponse(
            access_token=create_access_token(user.id),
            token_type="bearer",
        )