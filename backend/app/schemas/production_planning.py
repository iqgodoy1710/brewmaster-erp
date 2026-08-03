from decimal import Decimal

from pydantic import BaseModel


class RawMaterialPlanningProjectionResponse(BaseModel):
    raw_material_id: int
    raw_material_code: str
    raw_material_name: str
    unit_symbol: str
    current_stock: Decimal
    planned_consumption: Decimal
    projected_available_stock: Decimal
    has_shortage: bool