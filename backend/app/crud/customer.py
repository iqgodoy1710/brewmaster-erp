from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate


def get_customers(db: Session) -> list[Customer]:
    return (
        db.query(Customer)
        .filter(Customer.active.is_(True))
        .all()
    )


def get_customer_by_code(
    db: Session,
    code: str,
) -> Customer | None:
    return (
        db.query(Customer)
        .filter(Customer.code == code)
        .first()
    )


def get_customer_by_tax_id(
    db: Session,
    tax_id: str,
) -> Customer | None:
    return (
        db.query(Customer)
        .filter(Customer.tax_id == tax_id)
        .first()
    )


def get_customer_by_id(
    db: Session,
    customer_id: int,
) -> Customer | None:
    return (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )


def create_customer(
    db: Session,
    customer_data: CustomerCreate,
    code: str,
) -> Customer:
    customer = Customer(
        code=code,
        **customer_data.model_dump(),
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer