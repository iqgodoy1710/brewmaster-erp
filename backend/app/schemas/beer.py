from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BeerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    style: str | None = Field(default=None, max_length=50)
    description: str | None = None


class BeerCreate(BeerBase):
    model_config = ConfigDict(extra="forbid")
    minimum_stock_liters: Decimal = Field(
        default=Decimal("0.000"),
        ge=0,
    )


class BeerResponse(BeerBase):
    id: int
    code: str
    active: bool
    created_at: datetime
    updated_at: datetime
    minimum_stock_liters: Decimal 

    model_config = ConfigDict(from_attributes=True)

class BeerMinimumStockUpdate(BaseModel):
    minimum_stock_liters: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=3,
    )

    model_config = ConfigDict(extra="forbid")