from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel


class Supplier(BaseModel):
    __tablename__ = "suppliers"

    name = Column(String(100), nullable=False, unique=True)
    tax_id = Column(String(30), unique=True)
    email = Column(String(100))
    phone = Column(String(30))
    address = Column(String(255))
    notes = Column(Text)

    stock_movements = relationship(
        "RawMaterialStockMovement",
        back_populates="supplier",
    )