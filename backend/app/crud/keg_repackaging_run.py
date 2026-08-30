from datetime import datetime
from decimal import Decimal

from app.models.keg_repackaging_run import KegRepackagingRun
from sqlalchemy.orm import Session


def get_keg_repackaging_runs(
    db: Session,
) -> list[KegRepackagingRun]:
    return (
        db.query(KegRepackagingRun)
        .filter(KegRepackagingRun.active.is_(True))
        .order_by(
            KegRepackagingRun.occurred_at.desc(),
            KegRepackagingRun.id.desc(),
        )
        .all()
    )


def create_keg_repackaging_run(
    db: Session,
    *,
    code: str,
    keg_id: int,
    source_beer_presentation_id: int,
    target_beer_presentation_id: int,
    production_batch_id: int,
    packaged_quantity: int,
    packaged_volume_liters: Decimal,
    remaining_volume_liters: Decimal,
    waste_volume_liters: Decimal,
    performed_by_user_id: int | None,
    notes: str | None,
    occurred_at: datetime | None,
) -> KegRepackagingRun:
    repackaging_run = KegRepackagingRun(
        code=code,
        keg_id=keg_id,
        source_beer_presentation_id=source_beer_presentation_id,
        target_beer_presentation_id=target_beer_presentation_id,
        production_batch_id=production_batch_id,
        packaged_quantity=packaged_quantity,
        packaged_volume_liters=packaged_volume_liters,
        remaining_volume_liters=remaining_volume_liters,
        waste_volume_liters=waste_volume_liters,
        performed_by_user_id=performed_by_user_id,
        notes=notes,
        occurred_at=occurred_at,
    )

    db.add(repackaging_run)
    db.flush()

    return repackaging_run

def get_keg_repackaging_runs_by_keg(
    db: Session,
    keg_id: int,
) -> list[KegRepackagingRun]:
    return (
        db.query(KegRepackagingRun)
        .filter(
            KegRepackagingRun.keg_id == keg_id,
            KegRepackagingRun.active.is_(True),
        )
        .order_by(
            KegRepackagingRun.occurred_at.desc(),
            KegRepackagingRun.id.desc(),
        )
        .all()
    )