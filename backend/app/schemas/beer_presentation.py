from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BeerPresentationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    beer_id: int = Field(..., gt=0)
    packaging_format_id: int = Field(..., gt=0)
    minimum_stock: int = Field(default=0, ge=0)
    description: str | None = None


class BeerPresentationCreate(BeerPresentationBase):
    model_config = ConfigDict(extra="forbid")


class BeerPresentationMinimumStockUpdate(BaseModel):
    minimum_stock: int = Field(..., ge=0)

    model_config = ConfigDict(extra="forbid")


class BeerPresentationResponse(BeerPresentationBase):
    id: int
    code: str
    active: bool
    created_at: datetime
    updated_at: datetime
    current_stock: int

    model_config = ConfigDict(from_attributes=True)