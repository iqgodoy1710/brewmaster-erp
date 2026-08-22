from sqlalchemy.orm import Session

from app.models.customer_payment import CustomerPayment
from app.schemas.customer_payment import CustomerPaymentCreate


def get_customer_payments(
    db: Session,
    customer_id: int,
) -> list[CustomerPayment]:
    return (
        db.query(CustomerPayment)
        .filter(
            CustomerPayment.customer_id == customer_id,
            CustomerPayment.active.is_(True),
        )
        .order_by(
            CustomerPayment.occurred_at.desc(),
            CustomerPayment.id.desc(),
        )
        .all()
    )


def create_customer_payment(
    db: Session,
    payment_data: CustomerPaymentCreate,
    code: str,
) -> CustomerPayment:
    payment = CustomerPayment(
        code=code,
        **payment_data.model_dump(exclude_none=True),
    )

    db.add(payment)
    db.flush()

    return payment