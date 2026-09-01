from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel
from app.models.enums import DeliveryOrderStatus


class DeliveryOrder(BaseModel):
    __tablename__ = "delivery_orders"

    code = Column(String(30), nullable=False, unique=True)
    delivery_note_code = Column(String(30), unique=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
    )
    status = Column(
        Enum(
            DeliveryOrderStatus,
            name="delivery_order_status",
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        nullable=False,
        default=DeliveryOrderStatus.DRAFT,
        server_default=DeliveryOrderStatus.DRAFT.value,
    )
    notes = Column(Text)
    delivered_at = Column(TIMESTAMP, nullable=True)
    delivered_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )
    closed_at = Column(TIMESTAMP, nullable=True)
    closed_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    customer = relationship("Customer")
    items = relationship(
        "DeliveryOrderItem",
        back_populates="delivery_order",
    )
    kegs = relationship(
        "DeliveryOrderKeg",
        back_populates="delivery_order",
    )
    sale = relationship(
        "Sale",
        back_populates="delivery_order",
        uselist=False,
    )


class DeliveryOrderItem(BaseModel):
    __tablename__ = "delivery_order_items"

    __table_args__ = (
        CheckConstraint(
            "requested_quantity > 0",
            name="ck_delivery_order_items_requested_quantity_positive",
        ),
        CheckConstraint(
            "picked_quantity >= 0",
            name="ck_delivery_order_items_picked_quantity_non_negative",
        ),
        CheckConstraint(
            "delivered_quantity >= 0",
            name="ck_delivery_order_items_delivered_quantity_non_negative",
        ),
        CheckConstraint(
            "picked_quantity <= requested_quantity",
            name="ck_delivery_order_items_picked_quantity_not_above_requested",
        ),
        CheckConstraint(
            "delivered_quantity <= picked_quantity",
            name="ck_delivery_order_items_delivered_quantity_not_above_picked",
        ),
        UniqueConstraint(
            "delivery_order_id",
            "beer_presentation_id",
            name="uq_delivery_order_items_order_presentation",
        ),
    )

    delivery_order_id = Column(
        Integer,
        ForeignKey("delivery_orders.id"),
        nullable=False,
    )
    beer_presentation_id = Column(
        Integer,
        ForeignKey("beer_presentations.id"),
        nullable=False,
    )
    requested_quantity = Column(Integer, nullable=False)
    picked_quantity = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    delivered_quantity = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    notes = Column(Text)

    delivery_order = relationship(
        "DeliveryOrder",
        back_populates="items",
    )
    beer_presentation = relationship("BeerPresentation")


class DeliveryOrderKeg(BaseModel):
    __tablename__ = "delivery_order_kegs"

    __table_args__ = (
        UniqueConstraint(
            "delivery_order_id",
            "keg_id",
            name="uq_delivery_order_kegs_order_keg",
        ),
    )

    delivery_order_id = Column(
        Integer,
        ForeignKey("delivery_orders.id"),
        nullable=False,
    )
    keg_id = Column(
        Integer,
        ForeignKey("kegs.id"),
        nullable=False,
    )

    delivery_order = relationship(
        "DeliveryOrder",
        back_populates="kegs",
    )
    keg = relationship("Keg")