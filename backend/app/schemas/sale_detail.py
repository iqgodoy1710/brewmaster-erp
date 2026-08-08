from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import SaleStatus


class SaleDetailItemResponse(BaseModel):
    beer_presentation_id: int
    beer_presentation_code: str
    beer_presentation_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class SaleDetailResponse(BaseModel):
    id: int
    code: str
    customer_id: int
    customer_name: str
    status: SaleStatus
    notes: str | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    created_at: datetime
    updated_at: datetime
    items: list[SaleDetailItemResponse]
    total_amount: Decimal