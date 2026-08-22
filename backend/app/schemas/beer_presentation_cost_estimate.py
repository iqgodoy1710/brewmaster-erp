from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class BeerPresentationCostComponentResponse(BaseModel):
    component_type: Literal["beer", "packaging"]
    raw_material_id: int
    raw_material_code: str
    raw_material_name: str
    unit_symbol: str
    quantity: Decimal
    unit_cost: Decimal
    subtotal: Decimal


class BeerPresentationCostEstimateResponse(BaseModel):
    beer_presentation_id: int
    beer_presentation_code: str
    beer_presentation_name: str
    packaging_volume_liters: Decimal
    recipe_id: int
    recipe_version: int
    recipe_target_volume_liters: Decimal
    beer_cost: Decimal
    packaging_material_cost: Decimal
    total_unit_cost: Decimal
    components: list[BeerPresentationCostComponentResponse]