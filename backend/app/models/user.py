from sqlalchemy import Column, Enum, String

from app.common.base_model import BaseModel
from app.models.enums import UserRole


class User(BaseModel):
    __tablename__ = "users"

    username = Column(
        String(50),
        nullable=False,
        unique=True,
    )
    full_name = Column(
        String(150),
        nullable=False,
    )
    password_hash = Column(
        String(255),
        nullable=False,
    )
    role = Column(
        Enum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
        default=UserRole.OPERATOR,
    )
