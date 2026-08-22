from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BeerPresentationPriceCreate(BaseModel):
    beer_presentation_id: int = Field(..., gt=0)
    unit_price: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class BeerPresentationPriceResponse(
    BeerPresentationPriceCreate
):
    id: int
    effective_from: datetime
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)