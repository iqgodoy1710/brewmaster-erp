from app.models.enums import SaleStatus
from app.models.sale import Sale
from app.schemas.sale import SaleCreate
from sqlalchemy.orm import Session
from sqlalchemy.sql import func


def get_sales(db: Session) -> list[Sale]:
    return (
        db.query(Sale)
        .filter(Sale.active.is_(True))
        .all()
    )


def get_sale_by_code(
    db: Session,
    code: str,
) -> Sale | None:
    return (
        db.query(Sale)
        .filter(Sale.code == code)
        .first()
    )


def get_sale_by_id(
    db: Session,
    sale_id: int,
) -> Sale | None:
    return (
        db.query(Sale)
        .filter(Sale.id == sale_id)
        .first()
    )


def create_sale(
    db: Session,
    sale_data: SaleCreate,
) -> Sale:
    sale = Sale(**sale_data.model_dump())

    db.add(sale)
    db.commit()
    db.refresh(sale)

    return sale


def complete_sale(
    db: Session,
    sale: Sale,
) -> Sale:
    sale.status = SaleStatus.COMPLETED
    sale.completed_at = func.now()

    db.flush()

    return sale