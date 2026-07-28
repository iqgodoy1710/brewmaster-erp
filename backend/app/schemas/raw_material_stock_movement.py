from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RawMaterialMovementType


class RawMaterialStockMovementCreate(BaseModel):
    raw_material_id: int = Field(..., gt=0)
    movement_type: RawMaterialMovementType
    quantity: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=3,
    )
    supplier_id: int | None = Field(default=None, gt=0)
    unit_cost: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2,
    )
    reference: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    occurred_at: datetime | None = None


class RawMaterialStockMovementResponse(
    RawMaterialStockMovementCreate
):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)