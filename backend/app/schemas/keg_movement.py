from datetime import datetime
from decimal import Decimal

from app.models.enums import (
    KegMovementType,
    KegStatus,
)
from pydantic import BaseModel, ConfigDict, Field


class KegFillCreate(BaseModel):
    keg_id: int = Field(..., gt=0)
    packaging_run_id: int = Field(..., gt=0)
    notes: str | None = None
    occurred_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")

class KegFillFromBulkCreate(BaseModel):
    keg_id: int = Field(..., gt=0)
    production_batch_id: int = Field(..., gt=0)
    beer_presentation_id: int = Field(..., gt=0)
    notes: str | None = None
    occurred_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")

class KegMovementResponse(BaseModel):
    id: int
    keg_id: int
    movement_type: KegMovementType
    previous_status: KegStatus
    new_status: KegStatus
    resulting_volume_liters: Decimal
    beer_presentation_id: int | None
    production_batch_id: int | None
    packaging_run_id: int | None
    sale_id: int | None
    customer_id: int | None
    performed_by_user_id: int | None
    performed_by_username: str | None
    reference: str | None
    notes: str | None
    occurred_at: datetime
    active: bool
    created_at: datetime
    updated_at: datetime
    

    model_config = ConfigDict(from_attributes=True)


class KegReturnCreate(BaseModel):
    keg_id: int = Field(..., gt=0)
    resulting_volume_liters: Decimal = Field(..., ge=0)
    notes: str | None = None
    occurred_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")

class KegWashCreate(BaseModel):
    keg_id: int = Field(..., gt=0)
    notes: str | None = None
    occurred_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")

class KegRemnantTransferCreate(BaseModel):
    source_keg_ids: list[int] = Field(
        ...,
        min_length=1,
    )
    notes: str | None = None
    occurred_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")

class KegRemnantTransferResponse(BaseModel):
    production_batch_id: int
    recovered_volume_liters: Decimal
    resulting_available_bulk_volume_liters: Decimal
    source_movements: list[KegMovementResponse]

    model_config = ConfigDict(from_attributes=True)