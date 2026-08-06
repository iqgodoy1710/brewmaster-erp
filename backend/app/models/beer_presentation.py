from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel


class BeerPresentation(BaseModel):
    __tablename__ = "beer_presentations"

    __table_args__ = (
        UniqueConstraint(
            "beer_id",
            "packaging_format_id",
            name="uq_beer_presentations_beer_id_packaging_format_id",
        ),
        CheckConstraint(
            "current_stock >= 0",
            name="ck_beer_presentations_current_stock_non_negative",
        ),
    )

    code = Column(String(30), nullable=False, unique=True)
    name = Column(String(150), nullable=False, unique=True)
    beer_id = Column(
        Integer,
        ForeignKey("beers.id"),
        nullable=False,
    )
    packaging_format_id = Column(
        Integer,
        ForeignKey("packaging_formats.id"),
        nullable=False,
    )
    description = Column(Text)

    current_stock = Column(
        Integer,
        nullable=False,
        server_default="0",
    )

    beer = relationship(
        "Beer",
        back_populates="presentations",
    )
    packaging_format = relationship(
        "PackagingFormat",
        back_populates="beer_presentations",
    )

    packaging_materials = relationship(
        "BeerPresentationPackagingMaterial",
        back_populates="beer_presentation",
    )

    packaging_runs = relationship(
        "PackagingRun",
        back_populates="beer_presentation",
    )

    stock_movements = relationship(
        "BeerPresentationStockMovement",
        back_populates="beer_presentation",
    )
