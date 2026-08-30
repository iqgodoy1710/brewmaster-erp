from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class KegRepackagingRunCreate(BaseModel):
    keg_id: int = Field(..., gt=0)
    target_beer_presentation_id: int = Field(..., gt=0)
    packaged_quantity: int = Field(..., gt=0)
    remaining_volume_liters: Decimal = Field(..., ge=0)
    notes: str | None = None
    occurred_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class KegRepackagingRunResponse(BaseModel):
    id: int
    code: str
    keg_id: int
    source_beer_presentation_id: int
    target_beer_presentation_id: int
    production_batch_id: int
    packaged_quantity: int
    packaged_volume_liters: Decimal
    remaining_volume_liters: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=3,
    )
    waste_volume_liters: Decimal
    performed_by_user_id: int | None
    occurred_at: datetime
    notes: str | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
