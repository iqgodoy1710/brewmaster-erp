from sqlalchemy.orm import Session

from app.models.beer_presentation_price import (
    BeerPresentationPrice,
)
from app.schemas.beer_presentation_price import (
    BeerPresentationPriceCreate,
)


def get_beer_presentation_prices(
    db: Session,
    beer_presentation_id: int,
) -> list[BeerPresentationPrice]:
    return (
        db.query(BeerPresentationPrice)
        .filter(
            BeerPresentationPrice.beer_presentation_id
            == beer_presentation_id
        )
        .order_by(
            BeerPresentationPrice.effective_from.desc(),
            BeerPresentationPrice.id.desc(),
        )
        .all()
    )


def get_active_beer_presentation_price(
    db: Session,
    beer_presentation_id: int,
) -> BeerPresentationPrice | None:
    return (
        db.query(BeerPresentationPrice)
        .filter(
            BeerPresentationPrice.beer_presentation_id
            == beer_presentation_id,
            BeerPresentationPrice.active.is_(True),
        )
        .first()
    )


def create_beer_presentation_price(
    db: Session,
    price_data: BeerPresentationPriceCreate,
) -> BeerPresentationPrice:
    price = BeerPresentationPrice(
        **price_data.model_dump()
    )

    db.add(price)
    db.flush()

    return price


def deactivate_beer_presentation_price(
    db: Session,
    price: BeerPresentationPrice,
) -> BeerPresentationPrice:
    price.active = False

    db.flush()

    return price