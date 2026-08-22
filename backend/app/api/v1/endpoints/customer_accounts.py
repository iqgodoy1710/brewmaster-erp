from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.customer_account import CustomerAccountResponse
from app.schemas.customer_payment import (
    CustomerPaymentCreate,
    CustomerPaymentResponse,
)
from app.services.customer_account_service import CustomerAccountService
from app.services.customer_payment_service import CustomerPaymentService


router = APIRouter(
    tags=["Customer Accounts"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)


@router.get(
    "/customers/{customer_id}/account",
    response_model=CustomerAccountResponse,
)
def read_customer_account(
    customer_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return CustomerAccountService.get_by_customer(
        db,
        customer_id,
    )


@router.get(
    "/customers/{customer_id}/payments",
    response_model=list[CustomerPaymentResponse],
)
def read_customer_payments(
    customer_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return CustomerPaymentService.get_all_by_customer(
        db,
        customer_id,
    )


@router.post(
    "/customer-payments/",
    response_model=CustomerPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_payment(
    payment: CustomerPaymentCreate,
    db: Session = Depends(get_db),
):
    return CustomerPaymentService.create(db, payment)