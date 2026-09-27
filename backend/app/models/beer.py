from sqlalchemy import CheckConstraint, Column, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel


class Beer(BaseModel):
    __tablename__ = "beers"

    __table_args__ = (
        CheckConstraint(
            "minimum_stock_liters >= 0",
            name="ck_beers_minimum_stock_liters_non_negative",
        ),
    )

    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    style = Column(String(50))
    description = Column(Text)
    minimum_stock_liters = Column(
        Numeric(10, 3),
        nullable=False,
        server_default="0",
    )

    recipes = relationship(
        "Recipe",
        back_populates="beer",
    )

    presentations = relationship(
        "BeerPresentation",
        back_populates="beer",
    )
