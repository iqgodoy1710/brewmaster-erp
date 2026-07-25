from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel


class Category(BaseModel):
    __tablename__ = "raw_material_categories"    
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

    raw_materials = relationship(
        "RawMaterial",
        back_populates="category")    