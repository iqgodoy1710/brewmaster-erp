from sqlalchemy.orm import Session

from app.models.unit import Unit

from app.schemas.unit import UnitCreate

def get_units(db: Session):
    return (
        db.query(Unit)
        .filter(Unit.active.is_(True))
        .all()
    )


def get_unit_by_id(db: Session, unit_id: int) -> Unit | None:
    return (
        db.query(Unit)
        .filter(Unit.id == unit_id)
        .first()
    )

def get_unit_by_name(db: Session, name: str) -> Unit | None:
    return (
        db.query(Unit)
        .filter(Unit.name == name)
        .first()
    )


def get_unit_by_symbol(db: Session, symbol: str) -> Unit | None:
    return (
        db.query(Unit)
        .filter(Unit.symbol == symbol)
        .first()
    )


def create_unit(
    db: Session,
    unit_data: UnitCreate,
) -> Unit:
    unit = Unit(**unit_data.model_dump())

    db.add(unit)
    db.commit()
    db.refresh(unit)

    return unit