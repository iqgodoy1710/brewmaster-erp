from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel


class Recipe(BaseModel):
    __tablename__ = "recipes"

    __table_args__ = (
        CheckConstraint(
            "version > 0",
            name="ck_recipes_version_positive",
        ),
        CheckConstraint(
            "target_volume_liters > 0",
            name="ck_recipes_target_volume_liters_positive",
        ),
        UniqueConstraint(
            "beer_id",
            "version",
            name="uq_recipes_beer_id_version",
        ),
    )

    beer_id = Column(
        Integer,
        ForeignKey("beers.id"),
        nullable=False,
    )
    version = Column(Integer, nullable=False)
    target_volume_liters = Column(
        Numeric(10, 3),
        nullable=False,
    )
    notes = Column(Text)

    beer = relationship(
        "Beer",
        back_populates="recipes",
    )