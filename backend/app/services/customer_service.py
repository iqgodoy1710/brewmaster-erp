from sqlalchemy.orm import Session

from app.common.exceptions import (
    CustomerCodeAlreadyExistsError,
    CustomerTaxIdAlreadyExistsError,
)
from app.crud.customer import (
    create_customer,
    get_customer_by_code,
    get_customer_by_tax_id,
    get_customers,
)
from app.schemas.customer import CustomerCreate


class CustomerService:
    @staticmethod
    def get_all(db: Session):
        return get_customers(db)

    @staticmethod
    def create(
        db: Session,
        customer_data: CustomerCreate,
    ):
        existing_customer_by_code = get_customer_by_code(
            db,
            customer_data.code,
        )
        if existing_customer_by_code:
            raise CustomerCodeAlreadyExistsError(
                "A customer with this code already exists."
            )

        if customer_data.tax_id is not None:
            existing_customer_by_tax_id = get_customer_by_tax_id(
                db,
                customer_data.tax_id,
            )
            if existing_customer_by_tax_id:
                raise CustomerTaxIdAlreadyExistsError(
                    "A customer with this tax ID already exists."
                )

        return create_customer(db, customer_data)