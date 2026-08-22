from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional
from datetime import datetime


class RawMaterialBase(BaseModel):
    
    name: str = Field(..., max_length=100)
    category_id: int
    unit_id: int

    minimum_stock: Decimal = Field(default=0, ge=0)
    current_cost: Decimal = Field(default=0, ge=0)

    description: str | None = None


class RawMaterialCreate(RawMaterialBase):
    model_config = ConfigDict(extra="forbid")


class RawMaterialResponse(RawMaterialBase):
    id: int
    code: str

    active: bool

    created_at: datetime
    updated_at: datetime
    current_stock: Decimal

    model_config = ConfigDict(from_attributes=True)


class RawMaterialUpdate(BaseModel):
    
    name: Optional[str] = None

    category_id: Optional[int] = None
    unit_id: Optional[int] = None

    minimum_stock: Optional[Decimal] = Field(default=None, ge=0)

    current_cost: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    description: Optional[str] = None

    model_config = ConfigDict(extra="forbid")
