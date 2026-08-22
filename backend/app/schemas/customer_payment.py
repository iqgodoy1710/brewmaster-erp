from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CustomerPaymentMethod


class CustomerPaymentCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    amount: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    payment_method: CustomerPaymentMethod
    reference: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    occurred_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class CustomerPaymentResponse(CustomerPaymentCreate):
    id: int
    code: str
    active: bool
    created_at: datetime
    updated_at: datetime
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)