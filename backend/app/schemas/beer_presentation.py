from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BeerPresentationBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=150)
    beer_id: int = Field(..., gt=0)
    packaging_format_id: int = Field(..., gt=0)
    description: str | None = None


class BeerPresentationCreate(BeerPresentationBase):
    model_config = ConfigDict(extra="forbid")


class BeerPresentationResponse(BeerPresentationBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime
    current_stock: int

    model_config = ConfigDict(from_attributes=True)