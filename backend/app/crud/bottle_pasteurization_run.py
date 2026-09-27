from datetime import datetime

from app.models.bottle_pasteurization_run import (
    BottlePasteurizationRun,
)
from sqlalchemy.orm import Session


def get_bottle_pasteurization_runs(
    db: Session,
) -> list[BottlePasteurizationRun]:
    return (
        db.query(BottlePasteurizationRun)
        .filter(BottlePasteurizationRun.active.is_(True))
        .order_by(
            BottlePasteurizationRun.occurred_at.desc(),
            BottlePasteurizationRun.id.desc(),
        )
        .all()
    )


def create_bottle_pasteurization_run(
    db: Session,
    *,
    code: str,
    beer_presentation_id: int,
    processed_quantity: int,
    approved_quantity: int,
    waste_quantity: int,
    performed_by_user_id: int | None,
    notes: str | None,
    occurred_at: datetime | None,
) -> BottlePasteurizationRun:
    pasteurization_run = BottlePasteurizationRun(
        code=code,
        beer_presentation_id=beer_presentation_id,
        processed_quantity=processed_quantity,
        approved_quantity=approved_quantity,
        waste_quantity=waste_quantity,
        performed_by_user_id=performed_by_user_id,
        notes=notes,
        occurred_at=occurred_at,
    )

    db.add(pasteurization_run)
    db.flush()

    return pasteurization_run