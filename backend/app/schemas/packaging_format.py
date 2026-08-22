from datetime import datetime
from decimal import Decimal

from app.models.enums import PackagingFormatType
from pydantic import BaseModel, ConfigDict, Field


class PackagingFormatBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    capacity_liters: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=3,
    )
    description: str | None = None
    format_type: PackagingFormatType = PackagingFormatType.OTHER


class PackagingFormatCreate(PackagingFormatBase):
    model_config = ConfigDict(extra="forbid")


class PackagingFormatResponse(PackagingFormatBase):
    id: int
    code: str
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)