from decimal import Decimal

from app.models.sale_item import SaleItem
from app.schemas.sale_item import SaleItemCreate
from sqlalchemy.orm import Session


def get_sale_items(
    db: Session,
    sale_id: int,
) -> list[SaleItem]:
    return (
        db.query(SaleItem)
        .filter(
            SaleItem.sale_id == sale_id,
            SaleItem.active.is_(True),
        )
        .all()
    )


def get_sale_item_by_sale_id_and_beer_presentation_id(
    db: Session,
    sale_id: int,
    beer_presentation_id: int,
) -> SaleItem | None:
    return (
        db.query(SaleItem)
        .filter(
            SaleItem.sale_id == sale_id,
            SaleItem.beer_presentation_id == beer_presentation_id,
        )
        .first()
    )


def create_sale_item(
    db: Session,
    sale_item_data: SaleItemCreate,
    unit_price: Decimal,
) -> SaleItem:
    sale_item = SaleItem(
        **sale_item_data.model_dump(),
        unit_price=unit_price,
    )

    db.add(sale_item)
    db.commit()
    db.refresh(sale_item)

    return sale_item