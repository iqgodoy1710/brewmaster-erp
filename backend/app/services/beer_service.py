from app.common.exceptions import (
    BeerNameAlreadyExistsError,
)
from app.crud.beer import (
    create_beer,
    get_beer_by_code,
    get_beer_by_name,
    get_beers,
)
from app.schemas.beer import BeerCreate
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
