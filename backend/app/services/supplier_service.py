from app.common.exceptions import (
    SupplierNameAlreadyExistsError,
    SupplierTaxIdAlreadyExistsError,
)
from app.crud.supplier import (
    create_supplier,
    get_supplier_by_name,
    get_supplier_by_tax_id,
    get_suppliers,
)
from app.schemas.supplier import SupplierCreate
from sqlalchemy.orm import Session


class SupplierService:
    @staticmethod
    def get_all(db: Session):
        return get_suppliers(db)

    @staticmethod
    def create(
        db: Session,
        supplier_data: SupplierCreate,
    ):
        existing_name = get_supplier_by_name(db, supplier_data.name)
        if existing_name:
            raise SupplierNameAlreadyExistsError(
                "A supplier with this name already exists."
            )

        if supplier_data.tax_id is not None:
            existing_tax_id = get_supplier_by_tax_id(db, supplier_data.tax_id)
            if existing_tax_id:
                raise SupplierTaxIdAlreadyExistsError(
                    "A supplier with this tax ID already exists."
                )

        return create_supplier(db, supplier_data)