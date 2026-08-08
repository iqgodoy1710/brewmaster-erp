from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BeerPresentationStockMovementType


class BeerPresentationStockMovementCreate(BaseModel):
    beer_presentation_id: int = Field(..., gt=0)
    movement_type: BeerPresentationStockMovementType
    quantity: int = Field(..., gt=0)
    reference: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    occurred_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class BeerPresentationStockMovementResponse(
    BeerPresentationStockMovementCreate
):
    id: int
    packaging_run_id: int | None
    sale_id: int | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)