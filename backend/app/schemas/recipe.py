from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RecipeBase(BaseModel):
    beer_id: int = Field(..., gt=0)
    version: int = Field(..., gt=0)
    target_volume_liters: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=3,
    )
    notes: str | None = None


class RecipeCreate(RecipeBase):
    model_config = ConfigDict(extra="forbid")


class RecipeResponse(RecipeBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecipeUpdate(BaseModel):
    target_volume_liters: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=3,
    )
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")
