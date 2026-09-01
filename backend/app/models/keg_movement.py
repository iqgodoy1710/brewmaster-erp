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
from app.models.enums import KegMovementType, KegStatus


class KegMovement(BaseModel):
    __tablename__ = "keg_movements"

    __table_args__ = (
        CheckConstraint(
            "resulting_volume_liters >= 0",
            name="ck_keg_movements_resulting_volume_non_negative",
        ),
    )

    keg_id = Column(
        Integer,
        ForeignKey("kegs.id"),
        nullable=False,
    )
    movement_type = Column(
        Enum(
            KegMovementType,
            name="keg_movement_type",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
    )
    previous_status = Column(
        Enum(
            KegStatus,
            name="keg_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
    )
    new_status = Column(
        Enum(
            KegStatus,
            name="keg_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
    )
    resulting_volume_liters = Column(
        Numeric(10, 3),
        nullable=False,
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
    packaging_run_id = Column(
        Integer,
        ForeignKey("packaging_runs.id"),
        nullable=True,
    )
    keg_repackaging_run_id = Column(
        Integer,
        ForeignKey("keg_repackaging_runs.id"),
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
    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True,
    )
    performed_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )
    reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    occurred_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    keg = relationship(
        "Keg",
        back_populates="movements",
    )
    beer_presentation = relationship("BeerPresentation")
    production_batch = relationship("ProductionBatch")
    packaging_run = relationship("PackagingRun")
    sale = relationship("Sale")
    customer = relationship("Customer")
    performed_by_user = relationship("User")
    keg_repackaging_run = relationship(
        "KegRepackagingRun",
        back_populates="keg_movements",
    )
    delivery_order = relationship("DeliveryOrder")

    @property
    def performed_by_username(self) -> str | None:
        if not self.performed_by_user:
            return None

        return self.performed_by_user.username
