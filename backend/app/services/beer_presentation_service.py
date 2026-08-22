from app.common.exceptions import (
    BeerNotFoundError,
    BeerPresentationAlreadyExistsError,
    BeerPresentationNameAlreadyExistsError,
    BeerPresentationNotFoundError,
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
    get_beer_presentations_at_or_below_minimum_stock,
    update_beer_presentation_minimum_stock,
)
from app.crud.packaging_format import get_packaging_format_by_id
from app.schemas.beer_presentation import (
    BeerPresentationCreate,
    BeerPresentationMinimumStockUpdate,
)
from app.schemas.inventory_alert import (
    BeerPresentationLowStockResponse,
)
from app.services.code_service import generate_code
from sqlalchemy.orm import Session


class BeerPresentationService:
    @staticmethod
    def get_all(db: Session):
        return get_beer_presentations(db)

    @staticmethod
    def get_low_stock_alerts(
        db: Session,
    ) -> list[BeerPresentationLowStockResponse]:
        beer_presentations = (
            get_beer_presentations_at_or_below_minimum_stock(db)
        )

        return [
            BeerPresentationLowStockResponse(
                beer_presentation_id=beer_presentation.id,
                beer_presentation_code=beer_presentation.code,
                beer_presentation_name=beer_presentation.name,
                current_stock=beer_presentation.current_stock,
                minimum_stock=beer_presentation.minimum_stock,
                shortage_quantity=(
                    beer_presentation.minimum_stock
                    - beer_presentation.current_stock
                ),
            )
            for beer_presentation in beer_presentations
        ]

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

        generated_code = generate_code(
            db,
            "beer_presentation",
        )

        return create_beer_presentation(
            db,
            presentation_data,
            generated_code,
        )

    @staticmethod
    def update_minimum_stock(
        db: Session,
        code: str,
        minimum_stock_data: BeerPresentationMinimumStockUpdate,
    ):
        beer_presentation = get_beer_presentation_by_code(db, code)

        if not beer_presentation:
            raise BeerPresentationNotFoundError(
                "The beer presentation does not exist."
            )

        return update_beer_presentation_minimum_stock(
            db,
            beer_presentation,
            minimum_stock_data.minimum_stock,
        )