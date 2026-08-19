from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    user_data: UserCreate,
    password_hash: str,
) -> User:
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=password_hash,
        role=user_data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.full_name).all()


def get_active_administrator_count(
    db: Session,
) -> int:
    return (
        db.query(User)
        .filter(
            User.active.is_(True),
            User.role == UserRole.ADMIN,
        )
        .count()
    )


def update_user(
    db: Session,
    user: User,
    update_data: dict,
) -> User:
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user
