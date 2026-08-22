from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleItemCreate(BaseModel):
    sale_id: int = Field(..., gt=0)
    beer_presentation_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

    model_config = ConfigDict(extra="forbid")


class SaleItemResponse(SaleItemCreate):
    id: int
    unit_price: Decimal
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)