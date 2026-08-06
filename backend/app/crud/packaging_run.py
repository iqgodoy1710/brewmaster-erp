from decimal import Decimal

from app.models.packaging_run import PackagingRun
from app.schemas.packaging_run import PackagingRunCreate
from sqlalchemy.orm import Session


def get_packaging_runs(
    db: Session,
) -> list[PackagingRun]:
    return (
        db.query(PackagingRun)
        .filter(PackagingRun.active.is_(True))
        .all()
    )


def get_packaging_run_by_code(
    db: Session,
    code: str,
) -> PackagingRun | None:
    return (
        db.query(PackagingRun)
        .filter(PackagingRun.code == code)
        .first()
    )


def create_packaging_run(
    db: Session,
    packaging_run_data: PackagingRunCreate,
    packaged_volume_liters: Decimal,
) -> PackagingRun:
    packaging_run = PackagingRun(
        **packaging_run_data.model_dump(),
        packaged_volume_liters=packaged_volume_liters,
    )

    db.add(packaging_run)
    db.flush()

    return packaging_run