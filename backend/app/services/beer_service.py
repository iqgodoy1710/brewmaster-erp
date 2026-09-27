from app.common.exceptions import (
    BeerNameAlreadyExistsError,
    BeerNotFoundError,
)
from app.crud.beer import (
    create_beer,
    get_beer_by_code,
    get_beer_by_name,
    get_beers,
    update_beer_minimum_stock_liters,
)
from app.schemas.beer import BeerCreate, BeerMinimumStockUpdate
from app.services.code_service import generate_code
from sqlalchemy.orm import Session


class BeerService:
    @staticmethod
    def get_all(db: Session):
        return get_beers(db)

    @staticmethod
    def create(
        db: Session,
        beer_data: BeerCreate,
    ):
        existing_beer_by_name = get_beer_by_name(
            db,
            beer_data.name,
        )
        if existing_beer_by_name:
            raise BeerNameAlreadyExistsError("A beer with this name already exists.")

        return create_beer(
            db,
            beer_data,
            generate_code(db, "beer"),
        )

    @staticmethod
    def update_minimum_stock(
        db: Session,
        code: str,
        minimum_stock_data: BeerMinimumStockUpdate,
    ):
        beer = get_beer_by_code(
            db,
            code,
        )

        if not beer:
            raise BeerNotFoundError(
                "The beer does not exist."
            )

        return update_beer_minimum_stock_liters(
            db,
            beer,
            minimum_stock_data.minimum_stock_liters,
        )