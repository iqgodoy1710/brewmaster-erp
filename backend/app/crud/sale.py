from app.models.customer import Customer
from app.models.enums import SaleStatus
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.schemas.sale import SaleCreate
from sqlalchemy.orm import Session, joinedload
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
    code: str,
) -> Sale:
    sale = Sale(
        code=code,
        **sale_data.model_dump(),
    )

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

def cancel_sale(
    db: Session,
    sale: Sale,
    cancellation_reason: str | None,
) -> Sale:
    sale.status = SaleStatus.CANCELLED
    sale.cancelled_at = func.now()
    sale.cancellation_reason = cancellation_reason

    db.flush()

    return sale

def get_sale_detail_by_code(
    db: Session,
    code: str,
) -> Sale | None:
    return (
        db.query(Sale)
        .options(
            joinedload(Sale.customer),
            joinedload(Sale.items).joinedload(
                SaleItem.beer_presentation
            ),
        )
        .filter(Sale.code == code)
        .first()
    )

def get_completed_sales_report(
    db: Session,
):
    return (
        db.query(
            Sale.id.label("sale_id"),
            Sale.code.label("sale_code"),
            Customer.id.label("customer_id"),
            Customer.name.label("customer_name"),
            Sale.completed_at,
            func.sum(SaleItem.quantity).label("total_units"),
            func.sum(
                SaleItem.quantity * SaleItem.unit_price
            ).label("total_amount"),
        )
        .join(
            Customer,
            Sale.customer_id == Customer.id,
        )
        .join(
            SaleItem,
            SaleItem.sale_id == Sale.id,
        )
        .filter(
            Sale.active.is_(True),
            Sale.status == SaleStatus.COMPLETED,
            SaleItem.active.is_(True),
        )
        .group_by(
            Sale.id,
            Sale.code,
            Customer.id,
            Customer.name,
            Sale.completed_at,
        )
        .order_by(
            Sale.completed_at.desc(),
            Sale.id.desc(),
        )
        .all()
    )