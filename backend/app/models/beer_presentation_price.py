from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.common.base_model import BaseModel


class BeerPresentationPrice(BaseModel):
    __tablename__ = "beer_presentation_prices"

    __table_args__ = (
        CheckConstraint(
            "unit_price > 0",
            name="ck_beer_presentation_prices_unit_price_positive",
        ),
        Index(
            "uq_beer_presentation_prices_active_presentation",
            "beer_presentation_id",
            unique=True,
            postgresql_where=text("active = true"),
        ),
    )

    beer_presentation_id = Column(
        Integer,
        ForeignKey("beer_presentations.id"),
        nullable=False,
    )
    unit_price = Column(
        Numeric(10, 2),
        nullable=False,
    )
    effective_from = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )
    notes = Column(Text)

    beer_presentation = relationship(
        "BeerPresentation",
        back_populates="prices",
    )