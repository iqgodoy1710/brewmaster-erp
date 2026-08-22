from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.common.base_model import BaseModel
from app.models.enums import CustomerAccountMovementType


class CustomerAccountMovement(BaseModel):
    __tablename__ = "customer_account_movements"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_customer_account_movements_amount_positive",
        ),
        UniqueConstraint(
            "sale_id",
            "movement_type",
            name="uq_customer_account_movements_sale_id_type",
        ),
        UniqueConstraint(
            "payment_id",
            name="uq_customer_account_movements_payment_id",
        ),
        Index(
            "ix_customer_account_movements_customer_occurred_at",
            "customer_id",
            "occurred_at",
        ),
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
    )
    sale_id = Column(
        Integer,
        ForeignKey("sales.id"),
        nullable=True,
    )
    payment_id = Column(
        Integer,
        ForeignKey("customer_payments.id"),
        nullable=True,
    )
    movement_type = Column(
        Enum(
            CustomerAccountMovementType,
            name="customer_account_movement_type",
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        nullable=False,
    )
    amount = Column(Numeric(10, 2), nullable=False)
    reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    occurred_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    customer = relationship(
        "Customer",
        back_populates="account_movements",
    )
    sale = relationship(
        "Sale",
        back_populates="customer_account_movements",
    )
    payment = relationship(
        "CustomerPayment",
        back_populates="account_movements",
    )