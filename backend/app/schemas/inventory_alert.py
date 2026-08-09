from decimal import Decimal

from pydantic import BaseModel


class RawMaterialLowStockResponse(BaseModel):
    raw_material_id: int
    raw_material_code: str
    raw_material_name: str
    unit_symbol: str
    current_stock: Decimal
    minimum_stock: Decimal
    shortage_quantity: Decimal


class BeerPresentationLowStockResponse(BaseModel):
    beer_presentation_id: int
    beer_presentation_code: str
    beer_presentation_name: str
    current_stock: int
    minimum_stock: int
    shortage_quantity: int
