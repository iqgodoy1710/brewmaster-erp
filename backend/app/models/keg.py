from sqlalchemy import (
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel
from app.models.enums import KegFormFactor, KegStatus


class Keg(BaseModel):
    __tablename__ = "kegs"

    __table_args__ = (
        CheckConstraint(
            "current_volume_liters >= 0",
            name="ck_kegs_current_volume_non_negative",
        ),
    )

    code = Column(
        String(50),
        nullable=False,
        unique=True,
    )
    packaging_format_id = Column(
        Integer,
        ForeignKey("packaging_formats.id"),
        nullable=False,
    )
    form_factor = Column(
        Enum(
            KegFormFactor,
            name="keg_form_factor",
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        nullable=False,
        default=KegFormFactor.STANDARD,
        server_default=KegFormFactor.STANDARD.value,
    )
    status = Column(
        Enum(
            KegStatus,
            name="keg_status",
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        nullable=False,
        default=KegStatus.CLEAN_AVAILABLE,
        server_default=KegStatus.CLEAN_AVAILABLE.value,
    )
    current_volume_liters = Column(
        Numeric(10, 3),
        nullable=False,
        server_default="0",
    )
    beer_presentation_id = Column(
        Integer,
        ForeignKey("beer_presentations.id"),
        nullable=True,
    )
    production_batch_id = Column(
        Integer,
        ForeignKey("production_batches.id"),
        nullable=True,
    )
    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True,
    )
    notes = Column(Text, nullable=True)

    packaging_format = relationship("PackagingFormat")
    beer_presentation = relationship("BeerPresentation")
    production_batch = relationship("ProductionBatch")
    customer = relationship("Customer")
    movements = relationship(
    "KegMovement",
    back_populates="keg",
)