from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import KegFormFactor, KegStatus


class KegBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    packaging_format_id: int = Field(..., gt=0)
    form_factor: KegFormFactor = KegFormFactor.STANDARD
    notes: str | None = None


class KegCreate(KegBase):
    model_config = ConfigDict(extra="forbid")


class KegResponse(KegBase):
    id: int
    status: KegStatus
    current_volume_liters: Decimal
    beer_presentation_id: int | None
    production_batch_id: int | None
    customer_id: int | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)