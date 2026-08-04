from sqlalchemy.orm import Session

from app.common.exceptions import (
    BeerNotFoundError,
    BeerPresentationAlreadyExistsError,
    BeerPresentationCodeAlreadyExistsError,
    BeerPresentationNameAlreadyExistsError,
    InactiveBeerError,
    InactivePackagingFormatError,
    PackagingFormatNotFoundError,
)
from app.crud.beer import get_beer_by_id
from app.crud.beer_presentation import (
    create_beer_presentation,
    get_beer_presentation_by_beer_id_and_packaging_format_id,
    get_beer_presentation_by_code,
    get_beer_presentation_by_name,
    get_beer_presentations,
)
from app.crud.packaging_format import get_packaging_format_by_id
from app.schemas.beer_presentation import BeerPresentationCreate


class BeerPresentationService:
    @staticmethod
    def get_all(db: Session):
        return get_beer_presentations(db)

    @staticmethod
    def create(
        db: Session,
        presentation_data: BeerPresentationCreate,
    ):
        beer = get_beer_by_id(db, presentation_data.beer_id)
        if not beer:
            raise BeerNotFoundError("The beer does not exist.")

        if not beer.active:
            raise InactiveBeerError(
                "Cannot create a presentation for an inactive beer."
            )

        packaging_format = get_packaging_format_by_id(
            db,
            presentation_data.packaging_format_id,
        )
        if not packaging_format:
            raise PackagingFormatNotFoundError(
                "The packaging format does not exist."
            )

        if not packaging_format.active:
            raise InactivePackagingFormatError(
                "Cannot create a presentation for an inactive packaging format."
            )

        existing_presentation_by_code = get_beer_presentation_by_code(
            db,
            presentation_data.code,
        )
        if existing_presentation_by_code:
            raise BeerPresentationCodeAlreadyExistsError(
                "A beer presentation with this code already exists."
            )

        existing_presentation_by_name = get_beer_presentation_by_name(
            db,
            presentation_data.name,
        )
        if existing_presentation_by_name:
            raise BeerPresentationNameAlreadyExistsError(
                "A beer presentation with this name already exists."
            )

        existing_presentation = (
            get_beer_presentation_by_beer_id_and_packaging_format_id(
                db,
                presentation_data.beer_id,
                presentation_data.packaging_format_id,
            )
        )
        if existing_presentation:
            raise BeerPresentationAlreadyExistsError(
                "A presentation already exists for this beer and packaging format."
            )

        return create_beer_presentation(db, presentation_data)