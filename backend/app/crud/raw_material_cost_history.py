from decimal import Decimal

from app.models.enums import RawMaterialCostChangeSource
from app.models.raw_material_cost_history import RawMaterialCostHistory
from sqlalchemy.orm import Session


def create_raw_material_cost_history(
    db: Session,
    *,
    raw_material_id: int,
    previous_cost: Decimal,
    new_cost: Decimal,
    source: RawMaterialCostChangeSource,
    stock_movement_id: int | None = None,
) -> RawMaterialCostHistory:
    cost_change = RawMaterialCostHistory(
        raw_material_id=raw_material_id,
        stock_movement_id=stock_movement_id,
        source=source,
        previous_cost=previous_cost,
        new_cost=new_cost,
    )

    db.add(cost_change)
    db.flush()

    return cost_change


def get_raw_material_cost_history(
    db: Session,
    raw_material_id: int,
) -> list[RawMaterialCostHistory]:
    return (
        db.query(RawMaterialCostHistory)
        .filter(
            RawMaterialCostHistory.raw_material_id == raw_material_id,
        )
        .order_by(
            RawMaterialCostHistory.occurred_at.desc(),
            RawMaterialCostHistory.id.desc(),
        )
        .all()
    )