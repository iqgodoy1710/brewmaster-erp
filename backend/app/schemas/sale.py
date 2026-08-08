from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SaleStatus


class SaleBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    customer_id: int = Field(..., gt=0)
    notes: str | None = None


class SaleCreate(SaleBase):
    model_config = ConfigDict(extra="forbid")


class SaleResponse(SaleBase):
    id: int
    active: bool
    status: SaleStatus
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)