from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.common.base_model import BaseModel
from app.models.enums import RawMaterialCostChangeSource


class RawMaterialCostHistory(BaseModel):
    __tablename__ = "raw_material_cost_history"

    __table_args__ = (
        CheckConstraint(
            "previous_cost >= 0",
            name="ck_raw_material_cost_history_previous_cost_non_negative",
        ),
        CheckConstraint(
            "new_cost >= 0",
            name="ck_raw_material_cost_history_new_cost_non_negative",
        ),
    )

    raw_material_id = Column(
        Integer,
        ForeignKey("raw_materials.id"),
        nullable=False,
    )
    stock_movement_id = Column(
        Integer,
        ForeignKey("raw_material_stock_movements.id"),
        nullable=True,
        unique=True,
    )
    source = Column(
        Enum(
            RawMaterialCostChangeSource,
            name="raw_material_cost_change_source",
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        nullable=False,
    )
    previous_cost = Column(Numeric(10, 2), nullable=False)
    new_cost = Column(Numeric(10, 2), nullable=False)
    occurred_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    raw_material = relationship(
        "RawMaterial",
        back_populates="cost_history",
    )
    stock_movement = relationship(
        "RawMaterialStockMovement",
        back_populates="cost_change",
    )