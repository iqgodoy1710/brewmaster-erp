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


class BeerPresentationPackagingMaterial(BaseModel):
    __tablename__ = "beer_presentation_packaging_materials"

    __table_args__ = (
        CheckConstraint(
            "required_quantity > 0",
            name=(
                "ck_bppm_required_quantity_positive"
            ),
        ),
        UniqueConstraint(
            "beer_presentation_id",
            "raw_material_id",
            name=(
                "uq_bppm_presentation_id_raw_material_id"
            ),
        ),
    )

    beer_presentation_id = Column(
        Integer,
        ForeignKey("beer_presentations.id"),
        nullable=False,
    )
    raw_material_id = Column(
        Integer,
        ForeignKey("raw_materials.id"),
        nullable=False,
    )
    required_quantity = Column(
        Numeric(10, 3),
        nullable=False,
    )

    beer_presentation = relationship(
        "BeerPresentation",
        back_populates="packaging_materials",
    )
    raw_material = relationship(
        "RawMaterial",
        back_populates="beer_presentation_packaging_materials",
    )