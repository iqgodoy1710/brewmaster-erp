from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional
from datetime import datetime


class RawMaterialBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    category_id: int
    unit_id: int

    current_stock: Decimal = Field(default=0, ge=0)
    minimum_stock: Decimal = Field(default=0, ge=0)
    current_cost: Decimal = Field(default=0, ge=0)

    description: str | None = None


class RawMaterialCreate(RawMaterialBase):
    pass


class RawMaterialResponse(RawMaterialBase):
    id: int

    active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RawMaterialUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None

    category_id: Optional[int] = None
    unit_id: Optional[int] = None

    current_stock: Optional[Decimal] = Field(default=None, ge=0)
    minimum_stock: Optional[Decimal] = Field(default=None, ge=0)
    current_cost: Optional[Decimal] = Field(default=None, ge=0)

    description: Optional[str] = None

class RawMaterialDesactivate(BaseModel):
    pass