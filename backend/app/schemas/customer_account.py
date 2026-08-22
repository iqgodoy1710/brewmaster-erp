from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import CustomerAccountMovementType


class CustomerAccountMovementResponse(BaseModel):
    id: int
    customer_id: int
    sale_id: int | None
    sale_code: str | None
    payment_id: int | None
    payment_code: str | None
    movement_type: CustomerAccountMovementType
    amount: Decimal
    reference: str | None
    notes: str | None
    occurred_at: datetime
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerAccountResponse(BaseModel):
    customer_id: int
    customer_code: str
    customer_name: str
    balance: Decimal
    movements: list[CustomerAccountMovementResponse]