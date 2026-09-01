from datetime import datetime
from decimal import Decimal

from app.models.enums import KegMovementType, KegStatus
from app.models.keg_movement import KegMovement
from sqlalchemy import func
from sqlalchemy.orm import Session


def get_keg_movements(
    db: Session,
    keg_id: int,
) -> list[KegMovement]:
    return (
        db.query(KegMovement)
        .filter(
            KegMovement.keg_id == keg_id,
            KegMovement.active.is_(True),
        )
        .order_by(
            KegMovement.occurred_at.desc(),
            KegMovement.id.desc(),
        )
        .all()
    )


def count_filling_movements_for_packaging_run(
    db: Session,
    packaging_run_id: int,
) -> int:
    return (
        db.query(func.count(KegMovement.id))
        .filter(
            KegMovement.packaging_run_id == packaging_run_id,
            KegMovement.movement_type == KegMovementType.FILLING,
            KegMovement.active.is_(True),
        )
        .scalar()
    )


def create_keg_movement(
    db: Session,
    keg_id: int,
    movement_type: KegMovementType,
    previous_status: KegStatus,
    new_status: KegStatus,
    resulting_volume_liters: Decimal,
    beer_presentation_id: int | None = None,
    production_batch_id: int | None = None,
    packaging_run_id: int | None = None,
    keg_repackaging_run_id: int | None = None,
    sale_id: int | None = None,
    delivery_order_id: int | None = None,
    customer_id: int | None = None,
    reference: str | None = None,
    notes: str | None = None,
    occurred_at: datetime | None = None,
    performed_by_user_id: int | None = None,
) -> KegMovement:
    movement = KegMovement(
        keg_id=keg_id,
        movement_type=movement_type,
        previous_status=previous_status,
        new_status=new_status,
        resulting_volume_liters=resulting_volume_liters,
        beer_presentation_id=beer_presentation_id,
        production_batch_id=production_batch_id,
        packaging_run_id=packaging_run_id,
        keg_repackaging_run_id=keg_repackaging_run_id,
        sale_id=sale_id,
        delivery_order_id=delivery_order_id,
        customer_id=customer_id,
        reference=reference,
        notes=notes,
        occurred_at=occurred_at,
        performed_by_user_id=performed_by_user_id,
    )

    db.add(movement)
    db.flush()

    return movement
