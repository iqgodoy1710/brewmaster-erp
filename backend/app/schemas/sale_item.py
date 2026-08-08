from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleItemBase(BaseModel):
    sale_id: int = Field(..., gt=0)
    beer_presentation_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2,
    )


class SaleItemCreate(SaleItemBase):
    model_config = ConfigDict(extra="forbid")


class SaleItemResponse(SaleItemBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)