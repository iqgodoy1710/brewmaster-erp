from sqlalchemy.orm import Session

from app.models.beer import Beer
from app.schemas.beer import BeerCreate
from app.models.beer_presentation import BeerPresentation
from app.models.enums import (
    KegStatus,
    ProductionBatchStatus,
)
from app.models.keg import Keg
from app.models.production_batch import ProductionBatch
from app.models.recipe import Recipe
from sqlalchemy import func


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
    code: str,
) -> Beer:
    beer = Beer(
        code=code,
        **beer_data.model_dump(),
    )

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

def update_beer_minimum_stock_liters(
    db: Session,
    beer: Beer,
    minimum_stock_liters,
) -> Beer:
    beer.minimum_stock_liters = minimum_stock_liters

    db.commit()
    db.refresh(beer)

    return beer

def get_beer_keg_stock_coverage(db: Session):
    available_keg_stock = (
        db.query(
            BeerPresentation.beer_id.label("beer_id"),
            func.sum(Keg.current_volume_liters).label(
                "available_keg_volume_liters"
            ),
        )
        .join(
            Keg,
            Keg.beer_presentation_id == BeerPresentation.id,
        )
        .filter(
            Keg.active.is_(True),
            Keg.status == KegStatus.FILLED,
        )
        .group_by(BeerPresentation.beer_id)
        .subquery()
    )

    in_production = (
        db.query(
            Recipe.beer_id.label("beer_id"),
            func.sum(
                ProductionBatch.planned_volume_liters
            ).label("in_production_volume_liters"),
        )
        .join(
            Recipe,
            ProductionBatch.recipe_id == Recipe.id,
        )
        .filter(
            ProductionBatch.active.is_(True),
            ProductionBatch.status
            == ProductionBatchStatus.IN_PROGRESS,
        )
        .group_by(Recipe.beer_id)
        .subquery()
    )

    return (
        db.query(
            Beer.id.label("beer_id"),
            Beer.name.label("beer_name"),
            Beer.minimum_stock_liters.label(
                "minimum_stock_liters"
            ),
            func.coalesce(
                available_keg_stock.c.available_keg_volume_liters,
                0,
            ).label("available_keg_volume_liters"),
            func.coalesce(
                in_production.c.in_production_volume_liters,
                0,
            ).label("in_production_volume_liters"),
        )
        .outerjoin(
            available_keg_stock,
            available_keg_stock.c.beer_id == Beer.id,
        )
        .outerjoin(
            in_production,
            in_production.c.beer_id == Beer.id,
        )
        .filter(Beer.active.is_(True))
        .order_by(Beer.name)
        .all()
    )