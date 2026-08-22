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
from app.models.enums import CustomerPaymentMethod


class CustomerPayment(BaseModel):
    __tablename__ = "customer_payments"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_customer_payments_amount_positive",
        ),
    )

    code = Column(String(30), nullable=False, unique=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
    )
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(
        Enum(
            CustomerPaymentMethod,
            name="customer_payment_method",
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        nullable=False,
    )
    reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    occurred_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    customer = relationship(
        "Customer",
        back_populates="payments",
    )
    account_movements = relationship(
        "CustomerAccountMovement",
        back_populates="payment",
    )