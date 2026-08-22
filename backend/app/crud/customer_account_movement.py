from sqlalchemy.orm import Session, joinedload

from app.models.customer_account_movement import (
    CustomerAccountMovement,
)
from app.models.enums import CustomerAccountMovementType


def get_customer_account_movements(
    db: Session,
    customer_id: int,
) -> list[CustomerAccountMovement]:
    return (
        db.query(CustomerAccountMovement)
        .options(
            joinedload(CustomerAccountMovement.sale),
            joinedload(CustomerAccountMovement.payment),
        )
        .filter(
            CustomerAccountMovement.customer_id == customer_id,
            CustomerAccountMovement.active.is_(True),
        )
        .order_by(
            CustomerAccountMovement.occurred_at.desc(),
            CustomerAccountMovement.id.desc(),
        )
        .all()
    )


def create_customer_account_movement(
    db: Session,
    customer_id: int,
    movement_type: CustomerAccountMovementType,
    amount,
    reference: str | None = None,
    notes: str | None = None,
    sale_id: int | None = None,
    payment_id: int | None = None,
    occurred_at=None,
) -> CustomerAccountMovement:
    movement = CustomerAccountMovement(
        customer_id=customer_id,
        sale_id=sale_id,
        payment_id=payment_id,
        movement_type=movement_type,
        amount=amount,
        reference=reference,
        notes=notes,
        **(
            {"occurred_at": occurred_at}
            if occurred_at is not None
            else {}
        ),
    )

    db.add(movement)
    db.flush()

    return movement