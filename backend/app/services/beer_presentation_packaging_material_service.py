from app.common.exceptions import (
    BeerPresentationNotFoundError,
    BeerPresentationPackagingMaterialAlreadyExistsError,
    InactiveBeerPresentationError,
    InactiveRawMaterialError,
    KegPresentationCannotHavePackagingMaterialsError,
    RawMaterialNotFoundError,
)
from app.crud.beer_presentation import get_beer_presentation_by_id
from app.crud.beer_presentation_packaging_material import (
    create_beer_presentation_packaging_material,
    get_beer_presentation_packaging_material_by_presentation_id_and_raw_material_id,
    get_beer_presentation_packaging_materials,
)
from app.crud.raw_material import get_raw_material_by_id
from app.models.enums import PackagingFormatType
from app.schemas.beer_presentation_packaging_material import (
    BeerPresentationPackagingMaterialCreate,
)
from sqlalchemy.orm import Session


class BeerPresentationPackagingMaterialService:
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

        return get_beer_presentation_packaging_materials(
            db,
            beer_presentation_id,
        )

    @staticmethod
    def create(
        db: Session,
        packaging_material_data: BeerPresentationPackagingMaterialCreate,
    ):
        beer_presentation = get_beer_presentation_by_id(
            db,
            packaging_material_data.beer_presentation_id,
        )
        if not beer_presentation:
            raise BeerPresentationNotFoundError(
                "The beer presentation does not exist."
            )

        if not beer_presentation.active:
            raise InactiveBeerPresentationError(
                "Cannot add packaging materials to an inactive beer presentation."
            )

        if (
            beer_presentation.packaging_format.format_type
            == PackagingFormatType.KEG
        ):
            raise KegPresentationCannotHavePackagingMaterialsError(
                "Keg presentations do not use packaging materials because "
                "physical kegs are reusable."
            )

        raw_material = get_raw_material_by_id(
            db,
            packaging_material_data.raw_material_id,
        )
        if not raw_material:
            raise RawMaterialNotFoundError(
                "The raw material does not exist."
            )

        if not raw_material.active:
            raise InactiveRawMaterialError(
                "Cannot add an inactive raw material as packaging material."
            )

        existing_packaging_material = (
            get_beer_presentation_packaging_material_by_presentation_id_and_raw_material_id(
                db,
                packaging_material_data.beer_presentation_id,
                packaging_material_data.raw_material_id,
            )
        )
        if existing_packaging_material:
            raise BeerPresentationPackagingMaterialAlreadyExistsError(
                "This raw material is already a packaging material of the beer presentation."
            )

        return create_beer_presentation_packaging_material(
            db,
            packaging_material_data,
        )