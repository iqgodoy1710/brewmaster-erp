from getpass import getpass

from app.db.database import SessionLocal
from app.models.enums import UserRole
from app.schemas.user import UserCreate
from app.services.user_service import UserService


def main() -> None:
    username = input("Administrator username: ").strip().lower()
    full_name = input("Administrator full name: ").strip()
    password = getpass("Password: ")
    password_confirmation = getpass("Confirm password: ")

    if password != password_confirmation:
        raise ValueError("Passwords do not match.")

    db = SessionLocal()

    try:
        user = UserService.create(
            db,
            UserCreate(
                username=username,
                full_name=full_name,
                password=password,
                role=UserRole.ADMIN,
            ),
        )
    finally:
        db.close()

    print(
        f"Administrator created: {user.username} "
        f"({user.role.value})"
    )


if __name__ == "__main__":
    main()