from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.common.base_model import BaseModel

class Unit(BaseModel):
    __tablename__ = "units"

    name = Column(String(50), nullable=False, unique=True)
    symbol = Column(String(10), nullable=False, unique=True)

    raw_materials = relationship(
        "RawMaterial",
        back_populates="unit"
    )