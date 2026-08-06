from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PackagingRunBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    production_batch_id: int = Field(..., gt=0)
    beer_presentation_id: int = Field(..., gt=0)
    packaged_quantity: int = Field(..., gt=0)
    notes: str | None = None


class PackagingRunCreate(PackagingRunBase):
    model_config = ConfigDict(extra="forbid")


class PackagingRunResponse(PackagingRunBase):
    id: int
    packaged_volume_liters: Decimal
    occurred_at: datetime
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)