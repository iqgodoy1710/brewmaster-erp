from decimal import Decimal

from app.models.enums import RawMaterialMovementType
from app.models.raw_material_stock_movement import (
    RawMaterialStockMovement,
)
from app.schemas.raw_material_stock_movement import (
    RawMaterialStockMovementCreate,
)
from sqlalchemy.orm import Session


def create_raw_material_stock_movement(
    db: Session,
    movement_data: RawMaterialStockMovementCreate,
) -> RawMaterialStockMovement:
    movement = RawMaterialStockMovement(
        **movement_data.model_dump(exclude_none=True)
    )

    db.add(movement)
    db.flush()

    return movement

def get_raw_material_stock_movements(
    db: Session,
    raw_material_id: int,
) -> list[RawMaterialStockMovement]:
    return (
        db.query(RawMaterialStockMovement)
        .filter(
            RawMaterialStockMovement.raw_material_id
            == raw_material_id
        )
        .order_by(
            RawMaterialStockMovement.occurred_at.desc(),
            RawMaterialStockMovement.id.desc(),
        )
        .all()
    )

def create_production_consumption_movement(
    db: Session,
    raw_material_id: int,
    production_batch_id: int,
    quantity: Decimal,
    reference: str,
    notes: str | None = None,
) -> RawMaterialStockMovement:
    movement = RawMaterialStockMovement(
        raw_material_id=raw_material_id,
        production_batch_id=production_batch_id,
        movement_type=RawMaterialMovementType.PRODUCTION_CONSUMPTION,
        quantity=quantity,
        reference=reference,
        notes=notes,
    )

    db.add(movement)
    db.flush()

    return movement

def create_packaging_material_consumption_movement(
    db: Session,
    raw_material_id: int,
    packaging_run_id: int,
    quantity: Decimal,
    reference: str,
    notes: str | None = None,
) -> RawMaterialStockMovement:
    movement = RawMaterialStockMovement(
        raw_material_id=raw_material_id,
        packaging_run_id=packaging_run_id,
        movement_type=RawMaterialMovementType.PRODUCTION_CONSUMPTION,
        quantity=quantity,
        reference=reference,
        notes=notes,
    )

    db.add(movement)
    db.flush()

    return movement