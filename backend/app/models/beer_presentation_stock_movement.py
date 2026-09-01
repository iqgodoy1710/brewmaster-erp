from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.common.base_model import BaseModel
from app.models.enums import BeerPresentationStockMovementType


class BeerPresentationStockMovement(BaseModel):
    __tablename__ = "beer_presentation_stock_movements"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_bpsm_quantity_positive",
        ),
    )

    beer_presentation_id = Column(
        Integer,
        ForeignKey("beer_presentations.id"),
        nullable=False,
    )
    packaging_run_id = Column(
        Integer,
        ForeignKey("packaging_runs.id"),
        nullable=True,
    )
    sale_id = Column(
        Integer,
        ForeignKey("sales.id"),
        nullable=True,
    )
    delivery_order_id = Column(
        Integer,
        ForeignKey("delivery_orders.id"),
        nullable=True,
    )
    keg_repackaging_run_id = Column(
        Integer,
        ForeignKey("keg_repackaging_runs.id"),
        nullable=True,
    )
    movement_type = Column(
        Enum(
            BeerPresentationStockMovementType,
            name="beer_presentation_stock_movement_type",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False)
    reference = Column(String(100))
    notes = Column(Text)
    occurred_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    beer_presentation = relationship(
        "BeerPresentation",
        back_populates="stock_movements",
    )
    packaging_run = relationship(
        "PackagingRun",
        back_populates="beer_presentation_stock_movements",
    )
    sale = relationship(
        "Sale",
        back_populates="beer_presentation_stock_movements",
    )
    keg_repackaging_run = relationship(
        "KegRepackagingRun",
        back_populates="beer_presentation_stock_movements",
    )
    delivery_order = relationship("DeliveryOrder")
