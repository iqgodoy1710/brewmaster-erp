from app.common.exceptions import (
    CustomerNotFoundError,
    InactiveCustomerError,
)
from app.crud.customer import get_customer_by_id
from app.crud.customer_account_movement import (
    create_customer_account_movement,
)
from app.crud.customer_payment import (
    create_customer_payment,
    get_customer_payments,
)
from app.models.enums import CustomerAccountMovementType
from app.schemas.customer_payment import CustomerPaymentCreate
from app.services.code_service import generate_code
from sqlalchemy.orm import Session


class CustomerPaymentService:
    @staticmethod
    def get_all_by_customer(
        db: Session,
        customer_id: int,
    ):
        customer = get_customer_by_id(db, customer_id)
        if not customer:
            raise CustomerNotFoundError("The customer does not exist.")

        return get_customer_payments(db, customer_id)

    @staticmethod
    def create(
        db: Session,
        payment_data: CustomerPaymentCreate,
    ):
        customer = get_customer_by_id(db, payment_data.customer_id)
        if not customer:
            raise CustomerNotFoundError("The customer does not exist.")

        if not customer.active:
            raise InactiveCustomerError(
                "Cannot register a payment for an inactive customer."
            )

        try:
            payment = create_customer_payment(
                db,
                payment_data,
                generate_code(db, "customer_payment"),
            )

            create_customer_account_movement(
                db,
                customer_id=customer.id,
                payment_id=payment.id,
                movement_type=CustomerAccountMovementType.PAYMENT,
                amount=payment.amount,
                reference=payment.code,
                notes=payment.notes,
                occurred_at=payment.occurred_at,
            )

            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(payment)

        return payment