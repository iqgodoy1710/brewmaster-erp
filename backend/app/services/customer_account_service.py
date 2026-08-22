from decimal import Decimal

from app.common.exceptions import CustomerNotFoundError
from app.crud.customer import get_customer_by_id
from app.crud.customer_account_movement import (
    get_customer_account_movements,
)
from app.models.enums import CustomerAccountMovementType
from app.schemas.customer_account import (
    CustomerAccountMovementResponse,
    CustomerAccountResponse,
)
from sqlalchemy.orm import Session


class CustomerAccountService:
    @staticmethod
    def get_by_customer(
        db: Session,
        customer_id: int,
    ) -> CustomerAccountResponse:
        customer = get_customer_by_id(db, customer_id)
        if not customer:
            raise CustomerNotFoundError("The customer does not exist.")

        movements = get_customer_account_movements(db, customer.id)

        balance = Decimal("0.00")
        response_movements = []

        for movement in movements:
            if (
                movement.movement_type
                == CustomerAccountMovementType.SALE_CHARGE
            ):
                balance += movement.amount
            else:
                balance -= movement.amount

            response_movements.append(
                CustomerAccountMovementResponse(
                    id=movement.id,
                    customer_id=movement.customer_id,
                    sale_id=movement.sale_id,
                    sale_code=(
                        movement.sale.code
                        if movement.sale
                        else None
                    ),
                    payment_id=movement.payment_id,
                    payment_code=(
                        movement.payment.code
                        if movement.payment
                        else None
                    ),
                    movement_type=movement.movement_type,
                    amount=movement.amount,
                    reference=movement.reference,
                    notes=movement.notes,
                    occurred_at=movement.occurred_at,
                    active=movement.active,
                    created_at=movement.created_at,
                    updated_at=movement.updated_at,
                )
            )

        return CustomerAccountResponse(
            customer_id=customer.id,
            customer_code=customer.code,
            customer_name=customer.name,
            balance=balance,
            movements=response_movements,
        )