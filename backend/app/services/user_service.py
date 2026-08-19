from app.common.exceptions import (
    InvalidUserUpdateError,
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import hash_password
from app.crud.user import (
    create_user,
    get_active_administrator_count,
    get_user_by_email,
    get_user_by_id,
    get_users,
    update_user,
)
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from sqlalchemy.orm import Session


class UserService:
    @staticmethod
    def get_all(db: Session):
        return get_users(db)

    @staticmethod
    def create(
        db: Session,
        user_data: UserCreate,
    ):
        normalized_email = user_data.email.strip().lower()

        existing_user = get_user_by_email(
            db,
            normalized_email,
        )
        if existing_user:
            raise UserEmailAlreadyExistsError(
                "A user with this email already exists."
            )

        normalized_user_data = user_data.model_copy(
            update={"email": normalized_email}
        )

        return create_user(
            db,
            normalized_user_data,
            hash_password(normalized_user_data.password),
        )

    @staticmethod
    def update(
        db: Session,
        user_id: int,
        user_data: UserUpdate,
        current_user: User,
    ):
        user = get_user_by_id(db, user_id)

        if not user:
            raise UserNotFoundError("The user does not exist.")

        update_data = user_data.model_dump(exclude_unset=True)

        if not update_data:
            raise InvalidUserUpdateError(
                "At least one field must be provided."
            )

        requested_role = update_data.get("role")
        requested_active = update_data.get("active")

        if user.id == current_user.id:
            if requested_active is False:
                raise InvalidUserUpdateError(
                    "You cannot deactivate your own account."
                )

            if (
                requested_role is not None
                and requested_role != UserRole.ADMIN
            ):
                raise InvalidUserUpdateError(
                    "You cannot remove your own administrator role."
                )

        removes_administrator = (
            user.role == UserRole.ADMIN
            and (
                requested_active is False
                or (
                    requested_role is not None
                    and requested_role != UserRole.ADMIN
                )
            )
        )

        if (
            removes_administrator
            and get_active_administrator_count(db) <= 1
        ):
            raise InvalidUserUpdateError(
                "At least one active administrator is required."
            )

        if "password" in update_data:
            update_data["password_hash"] = hash_password(
                update_data.pop("password")
            )

        return update_user(
            db,
            user,
            update_data,
        )