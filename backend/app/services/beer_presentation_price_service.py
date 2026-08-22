from sqlalchemy.orm import Session

from app.common.exceptions import (
    BeerPresentationNotFoundError,
    InactiveBeerPresentationError,
)
from app.crud.beer_presentation import (
    get_beer_presentation_by_id,
)
from app.crud.beer_presentation_price import (
    create_beer_presentation_price,
    deactivate_beer_presentation_price,
    get_active_beer_presentation_price,
    get_beer_presentation_prices,
)
from app.schemas.beer_presentation_price import (
    BeerPresentationPriceCreate,
)


class BeerPresentationPriceService:
    @staticmethod
    def get_all_by_beer_presentation(
        db: Session,
        beer_presentation_id: int,
    ):
        beer_presentation = get_beer_presentation_by_id(
            db,
            beer_presentation_id,
        )
        if not beer_presentation:
            raise BeerPresentationNotFoundError(
                "The beer presentation does not exist."
            )

        return get_beer_presentation_prices(
            db,
            beer_presentation_id,
        )

    @staticmethod
    def create(
        db: Session,
        price_data: BeerPresentationPriceCreate,
    ):
        beer_presentation = get_beer_presentation_by_id(
            db,
            price_data.beer_presentation_id,
        )
        if not beer_presentation:
            raise BeerPresentationNotFoundError(
                "The beer presentation does not exist."
            )

        if not beer_presentation.active:
            raise InactiveBeerPresentationError(
                "Cannot set a price for an inactive beer presentation."
            )

        try:
            current_price = get_active_beer_presentation_price(
                db,
                price_data.beer_presentation_id,
            )
            if current_price:
                deactivate_beer_presentation_price(
                    db,
                    current_price,
                )

            price = create_beer_presentation_price(
                db,
                price_data,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(price)

        return price