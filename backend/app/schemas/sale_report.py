from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SaleReportItemResponse(BaseModel):
    sale_id: int
    sale_code: str
    customer_id: int
    customer_name: str
    completed_at: datetime
    total_units: int
    total_amount: Decimal