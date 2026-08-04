from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel


class Beer(BaseModel):
    __tablename__ = "beers"

    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    style = Column(String(50))
    description = Column(Text)

    recipes = relationship(
        "Recipe",
        back_populates="beer",
    )

    presentations = relationship(
        "BeerPresentation",
        back_populates="beer",
    )
