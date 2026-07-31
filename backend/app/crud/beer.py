from sqlalchemy.orm import Session

from app.models.beer import Beer
from app.schemas.beer import BeerCreate


def get_beers(db: Session) -> list[Beer]:
    return (
        db.query(Beer)
        .filter(Beer.active.is_(True))
        .all()
    )


def get_beer_by_code(
    db: Session,
    code: str,
) -> Beer | None:
    return (
        db.query(Beer)
        .filter(Beer.code == code)
        .first()
    )


def get_beer_by_name(
    db: Session,
    name: str,
) -> Beer | None:
    return (
        db.query(Beer)
        .filter(Beer.name == name)
        .first()
    )


def create_beer(
    db: Session,
    beer_data: BeerCreate,
) -> Beer:
    beer = Beer(**beer_data.model_dump())

    db.add(beer)
    db.commit()
    db.refresh(beer)

    return beer


def get_beer_by_id(
    db: Session,
    beer_id: int,
) -> Beer | None:
    return (
        db.query(Beer)
        .filter(Beer.id == beer_id)
        .first()
    )