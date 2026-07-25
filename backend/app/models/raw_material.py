
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel


class RawMaterial(BaseModel):
    __tablename__ = "raw_materials"

    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)

    category_id = Column(
        Integer, ForeignKey("raw_material_categories.id"), nullable=False
    )
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)

    current_stock = Column(Numeric(10, 3), nullable=False, default=0)
    minimum_stock = Column(Numeric(10, 3), nullable=False, default=0)

    current_cost = Column(Numeric(10, 2), default=0, nullable=False)

    description = Column(Text)

    category = relationship("Category", back_populates="raw_materials")

    unit = relationship("Unit", back_populates="raw_materials")
