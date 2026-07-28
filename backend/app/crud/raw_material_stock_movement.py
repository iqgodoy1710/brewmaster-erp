from sqlalchemy.orm import Session

from app.models.raw_material_stock_movement import (
    RawMaterialStockMovement,
)
from app.schemas.raw_material_stock_movement import (
    RawMaterialStockMovementCreate,
)


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