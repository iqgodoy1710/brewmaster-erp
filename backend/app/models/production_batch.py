from sqlalchemy import (
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel
from app.models.enums import ProductionBatchStatus


class ProductionBatch(BaseModel):
    __tablename__ = "production_batches"

    __table_args__ = (
        CheckConstraint(
            "planned_volume_liters > 0",
            name="ck_production_batches_planned_volume_positive",
        ),
        CheckConstraint(
            "available_bulk_volume_liters >= 0",
            name="ck_production_batches_available_bulk_volume_non_negative",
        ),
        CheckConstraint(
            "produced_volume_liters IS NULL OR produced_volume_liters > 0",
            name="ck_production_batches_produced_volume_positive",
        ),
    )

    code = Column(String(30), nullable=False, unique=True)
    recipe_id = Column(
        Integer,
        ForeignKey("recipes.id"),
        nullable=False,
    )
    planned_volume_liters = Column(
        Numeric(10, 3),
        nullable=False,
    )
    produced_volume_liters = Column(
        Numeric(10, 3),
        nullable=True,
    )
    available_bulk_volume_liters = Column(
        Numeric(10, 3),
        nullable=False,
        default=0,
    )
    completed_at = Column(
        TIMESTAMP,
        nullable=True,
    )
    status = Column(
        Enum(
            ProductionBatchStatus,
            name="production_batch_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
        default=ProductionBatchStatus.PLANNED,
    )
    notes = Column(Text)

    recipe = relationship(
        "Recipe",
        back_populates="production_batches",
    )
    raw_material_stock_movements = relationship(
        "RawMaterialStockMovement",
        back_populates="production_batch",
    )
