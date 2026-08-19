from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UserRole


class UserCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    full_name: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.OPERATOR

    model_config = ConfigDict(extra="forbid")


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )
    role: UserRole | None = None
    active: bool | None = None

    model_config = ConfigDict(extra="forbid")
