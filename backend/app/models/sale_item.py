from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel


class SaleItem(BaseModel):
    __tablename__ = "sale_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_sale_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_sale_items_unit_price_non_negative",
        ),
        UniqueConstraint(
            "sale_id",
            "beer_presentation_id",
            name="uq_sale_items_sale_id_beer_presentation_id",
        ),
    )

    sale_id = Column(
        Integer,
        ForeignKey("sales.id"),
        nullable=False,
    )
    beer_presentation_id = Column(
        Integer,
        ForeignKey("beer_presentations.id"),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False)
    unit_price = Column(
        Numeric(10, 2),
        nullable=False,
    )

    sale = relationship(
        "Sale",
        back_populates="items",
    )
    beer_presentation = relationship(
        "BeerPresentation",
        back_populates="sale_items",
    )