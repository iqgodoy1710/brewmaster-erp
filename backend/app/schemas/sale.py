from datetime import datetime

from app.models.enums import SaleStatus
from pydantic import BaseModel, ConfigDict, Field


class SaleBase(BaseModel):
    customer_id: int = Field(..., gt=0)
    notes: str | None = None


class SaleCreate(SaleBase):
    model_config = ConfigDict(extra="forbid")


class SaleResponse(SaleBase):
    id: int
    code: str
    active: bool
    status: SaleStatus
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None
    cancellation_reason: str | None

    model_config = ConfigDict(from_attributes=True)

class SaleCancel(BaseModel):
    cancellation_reason: str | None = None

    model_config = ConfigDict(extra="forbid")

class SaleComplete(BaseModel):
    keg_ids: list[int] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")