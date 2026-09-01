from decimal import Decimal

from app.models.enums import KegFormFactor
from pydantic import BaseModel


class KegFinishedProductStockResponse(BaseModel):
    beer_id: int
    beer_name: str
    beer_style: str | None
    packaging_format_id: int
    packaging_format_name: str
    form_factor: KegFormFactor
    keg_count: int
    total_volume_liters: Decimal


class PackagedFinishedProductStockResponse(BaseModel):
    beer_presentation_id: int
    beer_presentation_code: str
    beer_presentation_name: str
    beer_name: str
    beer_style: str | None
    packaging_format_name: str
    current_stock: int
    total_volume_liters: Decimal