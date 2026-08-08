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