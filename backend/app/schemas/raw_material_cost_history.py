from datetime import datetime
from decimal import Decimal

from app.models.enums import RawMaterialCostChangeSource
from pydantic import BaseModel


class RawMaterialCostHistoryResponse(BaseModel):
    id: int
    raw_material_id: int
    stock_movement_id: int | None
    source: RawMaterialCostChangeSource
    previous_cost: Decimal
    new_cost: Decimal
    variation_amount: Decimal
    variation_percentage: Decimal | None
    occurred_at: datetime