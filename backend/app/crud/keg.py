from decimal import Decimal

from app.models.enums import KegStatus
from app.models.keg import Keg
from app.schemas.keg import KegCreate
from sqlalchemy.orm import Session


def get_kegs(db: Session) -> list[Keg]:
    return db.query(Keg).filter(Keg.active.is_(True)).order_by(Keg.code).all()


def get_keg_by_code(
    db: Session,
    code: str,
) -> Keg | None:
    return db.query(Keg).filter(Keg.code == code).first()


def create_keg(
    db: Session,
    keg_data: KegCreate,
    code: str,
) -> Keg:
    keg = Keg(
        code=code,
        packaging_format_id=keg_data.packaging_format_id,
        form_factor=keg_data.form_factor,
        notes=keg_data.notes,
    )

    db.add(keg)
    db.commit()
    db.refresh(keg)

    return keg


def get_keg_by_id(
    db: Session,
    keg_id: int,
) -> Keg | None:
    return db.query(Keg).filter(Keg.id == keg_id).first()


def update_keg_state(
    db: Session,
    keg: Keg,
    status: KegStatus,
    current_volume_liters: Decimal,
    beer_presentation_id: int | None,
    production_batch_id: int | None,
    customer_id: int | None,
) -> Keg:
    keg.status = status
    keg.current_volume_liters = current_volume_liters
    keg.beer_presentation_id = beer_presentation_id
    keg.production_batch_id = production_batch_id
    keg.customer_id = customer_id

    db.flush()

    return keg
