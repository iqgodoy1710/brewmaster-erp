from sqlalchemy import (
    TIMESTAMP,
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
from sqlalchemy.sql import func

from app.common.base_model import BaseModel
from app.models.enums import RawMaterialMovementType


class RawMaterialStockMovement(BaseModel):
    __tablename__ = "raw_material_stock_movements"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_raw_material_stock_movements_quantity_positive",
        ),
    )

    raw_material_id = Column(
        Integer,
        ForeignKey("raw_materials.id"),
        nullable=False,
    )
    production_batch_id = Column(
        Integer,
        ForeignKey("production_batches.id"),
        nullable=True,
    )
    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        nullable=True,
    )
    movement_type = Column(
        Enum(
            RawMaterialMovementType,
            name="raw_material_movement_type",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
    )
    quantity = Column(
        Numeric(10, 3),
        nullable=False,
    )
    unit_cost = Column(
        Numeric(10, 2),
        nullable=True,
    )
    reference = Column(String(100))
    notes = Column(Text)
    occurred_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    raw_material = relationship(
        "RawMaterial",
        back_populates="stock_movements",
    )
    supplier = relationship(
        "Supplier",
        back_populates="stock_movements",
    )
    production_batch = relationship(
        "ProductionBatch",
        back_populates="raw_material_stock_movements",
    )
