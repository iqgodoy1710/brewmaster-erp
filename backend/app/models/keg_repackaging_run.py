from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.common.base_model import BaseModel


class KegRepackagingRun(BaseModel):
    __tablename__ = "keg_repackaging_runs"

    __table_args__ = (
        CheckConstraint(
            "packaged_quantity > 0",
            name="ck_keg_repackaging_runs_packaged_quantity_positive",
        ),
        CheckConstraint(
            "packaged_volume_liters > 0",
            name="ck_keg_repackaging_runs_packaged_volume_positive",
        ),
        CheckConstraint(
            "remaining_volume_liters >= 0",
            name="ck_keg_repackaging_runs_remaining_volume_non_negative",
        ),
        CheckConstraint(
            "waste_volume_liters >= 0",
            name="ck_keg_repackaging_runs_waste_volume_non_negative",
        ),
    )

    code = Column(String(30), nullable=False, unique=True)
    keg_id = Column(
        Integer,
        ForeignKey("kegs.id"),
        nullable=False,
    )
    source_beer_presentation_id = Column(
        Integer,
        ForeignKey("beer_presentations.id"),
        nullable=False,
    )
    target_beer_presentation_id = Column(
        Integer,
        ForeignKey("beer_presentations.id"),
        nullable=False,
    )
    production_batch_id = Column(
        Integer,
        ForeignKey("production_batches.id"),
        nullable=False,
    )
    packaged_quantity = Column(Integer, nullable=False)
    packaged_volume_liters = Column(
        Numeric(10, 3),
        nullable=False,
    )
    remaining_volume_liters = Column(
        Numeric(10, 3),
        nullable=False,
    )
    waste_volume_liters = Column(
        Numeric(10, 3),
        nullable=False,
    )
    performed_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )
    occurred_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )
    notes = Column(Text, nullable=True)

    keg = relationship("Keg")
    source_beer_presentation = relationship(
        "BeerPresentation",
        foreign_keys=[source_beer_presentation_id],
    )
    target_beer_presentation = relationship(
        "BeerPresentation",
        foreign_keys=[target_beer_presentation_id],
    )
    production_batch = relationship("ProductionBatch")
    performed_by_user = relationship("User")
    beer_presentation_stock_movements = relationship(
        "BeerPresentationStockMovement",
        back_populates="keg_repackaging_run",
    )
    raw_material_stock_movements = relationship(
        "RawMaterialStockMovement",
        back_populates="keg_repackaging_run",
    )
    keg_movements = relationship(
        "KegMovement",
        back_populates="keg_repackaging_run",
    )
