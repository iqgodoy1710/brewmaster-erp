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


class PackagingRun(BaseModel):
    __tablename__ = "packaging_runs"

    __table_args__ = (
        CheckConstraint(
            "packaged_quantity > 0",
            name="ck_packaging_runs_packaged_quantity_positive",
        ),
        CheckConstraint(
            "packaged_volume_liters > 0",
            name="ck_packaging_runs_packaged_volume_positive",
        ),
    )

    code = Column(String(30), nullable=False, unique=True)
    production_batch_id = Column(
        Integer,
        ForeignKey("production_batches.id"),
        nullable=False,
    )
    beer_presentation_id = Column(
        Integer,
        ForeignKey("beer_presentations.id"),
        nullable=False,
    )
    packaged_quantity = Column(Integer, nullable=False)
    packaged_volume_liters = Column(
        Numeric(10, 3),
        nullable=False,
    )
    occurred_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )
    notes = Column(Text)

    production_batch = relationship(
        "ProductionBatch",
        back_populates="packaging_runs",
    )
    beer_presentation = relationship(
        "BeerPresentation",
        back_populates="packaging_runs",
    )
    raw_material_stock_movements = relationship(
        "RawMaterialStockMovement",
        back_populates="packaging_run",
    )

    beer_presentation_stock_movements = relationship(
        "BeerPresentationStockMovement",
        back_populates="packaging_run",
    )
