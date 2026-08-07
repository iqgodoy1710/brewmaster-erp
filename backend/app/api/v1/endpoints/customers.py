from app.db.dependencies import get_db
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.customer_service import CustomerService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.get("/", response_model=list[CustomerResponse])
def read_customers(
    db: Session = Depends(get_db),
):
    return CustomerService.get_all(db)


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
):
    return CustomerService.create(db, customer)