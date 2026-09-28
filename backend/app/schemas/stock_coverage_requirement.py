from decimal import Decimal

from pydantic import BaseModel


class StockCoverageRequirementResponse(BaseModel):
    raw_material_id: int
    raw_material_code: str
    raw_material_name: str
    unit_symbol: str
    production_required_quantity: Decimal
    packaging_required_quantity: Decimal
    total_required_quantity: Decimal
    current_stock: Decimal
    minimum_stock: Decimal
    projected_stock: Decimal
    shortage_quantity: Decimal
    has_shortage: bool


class StockCoverageWarningResponse(BaseModel):
    source_type: str
    source_code: str
    source_name: str
    detail: str


class StockCoveragePlanResponse(BaseModel):
    requirements: list[StockCoverageRequirementResponse]
    warnings: list[StockCoverageWarningResponse]