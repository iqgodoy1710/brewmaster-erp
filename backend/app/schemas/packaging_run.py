from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PackagingRunBase(BaseModel):
    production_batch_id: int = Field(..., gt=0)
    beer_presentation_id: int = Field(..., gt=0)
    packaged_quantity: int = Field(..., gt=0)
    notes: str | None = None


class PackagingRunCreate(PackagingRunBase):
    model_config = ConfigDict(extra="forbid")


class PackagingRunResponse(PackagingRunBase):
    id: int
    code: str
    packaged_volume_liters: Decimal
    occurred_at: datetime
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)