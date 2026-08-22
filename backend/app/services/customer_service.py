from app.common.exceptions import (
    CustomerTaxIdAlreadyExistsError,
)
from app.crud.customer import (
    create_customer,
    get_customer_by_tax_id,
    get_customers,
)
from app.schemas.customer import CustomerCreate
from app.services.code_service import generate_code
from sqlalchemy.orm import Session


class CustomerService:
    @staticmethod
    def get_all(db: Session):
        return get_customers(db)

    @staticmethod
    def create(
        db: Session,
        customer_data: CustomerCreate,
    ):

        if customer_data.tax_id is not None:
            existing_customer_by_tax_id = get_customer_by_tax_id(
                db,
                customer_data.tax_id,
            )
            if existing_customer_by_tax_id:
                raise CustomerTaxIdAlreadyExistsError(
                    "A customer with this tax ID already exists."
                )

        return create_customer(
            db,
            customer_data,
            generate_code(db, "customer"),
        )
