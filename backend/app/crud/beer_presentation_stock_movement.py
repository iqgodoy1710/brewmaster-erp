from app.models.beer_presentation_stock_movement import (
    BeerPresentationStockMovement,
)
from app.models.enums import BeerPresentationStockMovementType
from app.schemas.beer_presentation_stock_movement import (
    BeerPresentationStockMovementCreate,
)
from sqlalchemy.orm import Session


def get_beer_presentation_stock_movements(
    db: Session,
    beer_presentation_id: int,
) -> list[BeerPresentationStockMovement]:
    return (
        db.query(BeerPresentationStockMovement)
        .filter(
            BeerPresentationStockMovement.beer_presentation_id == beer_presentation_id
        )
        .order_by(
            BeerPresentationStockMovement.occurred_at.desc(),
            BeerPresentationStockMovement.id.desc(),
        )
        .all()
    )


def create_beer_presentation_stock_movement(
    db: Session,
    movement_data: BeerPresentationStockMovementCreate,
) -> BeerPresentationStockMovement:
    movement = BeerPresentationStockMovement(
        **movement_data.model_dump(exclude_none=True)
    )

    db.add(movement)
    db.flush()

    return movement


def create_packaging_receipt_movement(
    db: Session,
    beer_presentation_id: int,
    packaging_run_id: int,
    quantity: int,
    reference: str,
    notes: str | None = None,
) -> BeerPresentationStockMovement:
    movement = BeerPresentationStockMovement(
        beer_presentation_id=beer_presentation_id,
        packaging_run_id=packaging_run_id,
        movement_type=(BeerPresentationStockMovementType.PACKAGING_RECEIPT),
        quantity=quantity,
        reference=reference,
        notes=notes,
    )

    db.add(movement)
    db.flush()

    return movement


def create_sale_movement(
    db: Session,
    beer_presentation_id: int,
    sale_id: int,
    quantity: int,
    reference: str,
    notes: str | None = None,
) -> BeerPresentationStockMovement:
    movement = BeerPresentationStockMovement(
        beer_presentation_id=beer_presentation_id,
        sale_id=sale_id,
        movement_type=BeerPresentationStockMovementType.SALE,
        quantity=quantity,
        reference=reference,
        notes=notes,
    )

    db.add(movement)
    db.flush()

    return movement

def create_sale_cancellation_movement(
    db: Session,
    beer_presentation_id: int,
    sale_id: int,
    quantity: int,
    reference: str,
    notes: str | None = None,
) -> BeerPresentationStockMovement:
    movement = BeerPresentationStockMovement(
        beer_presentation_id=beer_presentation_id,
        sale_id=sale_id,
        movement_type=(
            BeerPresentationStockMovementType.INVENTORY_ADJUSTMENT_IN
        ),
        quantity=quantity,
        reference=reference,
        notes=notes,
    )

    db.add(movement)
    db.flush()

    return movement