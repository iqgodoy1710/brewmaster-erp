from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ProductionBatchStatus


class ProductionBatchBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    recipe_id: int = Field(..., gt=0)
    planned_volume_liters: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=3,
    )
    notes: str | None = None


class ProductionBatchCreate(ProductionBatchBase):
    model_config = ConfigDict(extra="forbid")


class ProductionBatchResponse(ProductionBatchBase):
    id: int
    active: bool
    status: ProductionBatchStatus
    available_bulk_volume_liters: Decimal
    produced_volume_liters: Decimal | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionBatchComplete(BaseModel):
    produced_volume_liters: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=3,
    )

    model_config = ConfigDict(extra="forbid")
