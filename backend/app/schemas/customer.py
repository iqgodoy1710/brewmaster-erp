from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=150)
    tax_id: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = None
    notes: str | None = None


class CustomerCreate(CustomerBase):
    model_config = ConfigDict(extra="forbid")


class CustomerResponse(CustomerBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)