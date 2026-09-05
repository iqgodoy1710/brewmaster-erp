from datetime import datetime
from decimal import Decimal

from app.models.enums import DeliveryOrderStatus
from pydantic import BaseModel, ConfigDict, Field


class DeliveryOrderCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class DeliveryOrderUpdate(BaseModel):
    customer_id: int | None = Field(default=None, gt=0)
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class DeliveryOrderItemCreate(BaseModel):
    beer_presentation_id: int = Field(..., gt=0)
    requested_quantity: int = Field(..., gt=0)
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class DeliveryOrderItemUpdate(BaseModel):
    requested_quantity: int | None = Field(default=None, gt=0)
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class DeliveryOrderPickingUpdate(BaseModel):
    picked_quantity: int = Field(..., ge=0)

    model_config = ConfigDict(extra="forbid")

class DeliveryOrderItemClose(BaseModel):
    requested_quantity: int = Field(..., gt=0)

    model_config = ConfigDict(extra="forbid")


class DeliveryOrderKegCreate(BaseModel):
    keg_id: int = Field(..., gt=0)

    model_config = ConfigDict(extra="forbid")


class DeliveryOrderDeliver(BaseModel):
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class DeliveryOrderCloseItem(BaseModel):
    delivery_order_item_id: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)


class DeliveryOrderClose(BaseModel):
    items: list[DeliveryOrderCloseItem] = Field(..., min_length=1)
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class DeliveryOrderItemResponse(BaseModel):
    id: int
    delivery_order_id: int
    beer_presentation_id: int
    requested_quantity: int
    picked_quantity: int
    delivered_quantity: int
    notes: str | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeliveryOrderKegResponse(BaseModel):
    id: int
    delivery_order_id: int
    keg_id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeliveryOrderResponse(BaseModel):
    id: int
    code: str
    delivery_note_code: str | None
    customer_id: int
    status: DeliveryOrderStatus
    notes: str | None
    delivered_at: datetime | None
    delivered_by_user_id: int | None
    closed_at: datetime | None
    closed_by_user_id: int | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeliveryOrderDetailResponse(DeliveryOrderResponse):
    items: list[DeliveryOrderItemResponse]
    kegs: list[DeliveryOrderKegResponse]