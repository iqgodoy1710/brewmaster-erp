from sqlalchemy.orm import Session

from app.models.supplier import Supplier

from app.schemas.supplier import SupplierCreate

def get_suppliers(db: Session):
    return (
        db.query(Supplier)
        .filter(Supplier.active.is_(True))
        .all()
    )


def get_supplier_by_name(db: Session, name: str) -> Supplier | None:
    return (
        db.query(Supplier)
        .filter(Supplier.name == name)
        .first()
    )

def get_supplier_by_tax_id(db: Session, tax_id: str) -> Supplier | None:
    return (
        db.query(Supplier)
        .filter(Supplier.tax_id == tax_id)
        .first()
    )


def create_supplier(
    db: Session,
    supplier_data: SupplierCreate,
) -> Supplier:
    supplier = Supplier(**supplier_data.model_dump())

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier