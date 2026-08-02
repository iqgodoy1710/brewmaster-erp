from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RecipeIngredientBase(BaseModel):
    recipe_id: int = Field(..., gt=0)
    raw_material_id: int = Field(..., gt=0)
    required_quantity: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=3,
    )


class RecipeIngredientCreate(RecipeIngredientBase):
    model_config = ConfigDict(extra="forbid")


class RecipeIngredientResponse(RecipeIngredientBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)