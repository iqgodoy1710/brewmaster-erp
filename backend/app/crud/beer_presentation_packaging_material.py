from sqlalchemy.orm import Session

from app.models.beer_presentation_packaging_material import (
    BeerPresentationPackagingMaterial,
)
from app.schemas.beer_presentation_packaging_material import (
    BeerPresentationPackagingMaterialCreate,
)


def get_beer_presentation_packaging_materials(
    db: Session,
    beer_presentation_id: int,
) -> list[BeerPresentationPackagingMaterial]:
    return (
        db.query(BeerPresentationPackagingMaterial)
        .filter(
            BeerPresentationPackagingMaterial.beer_presentation_id
            == beer_presentation_id,
            BeerPresentationPackagingMaterial.active.is_(True),
        )
        .all()
    )


def get_beer_presentation_packaging_material_by_presentation_id_and_raw_material_id(
    db: Session,
    beer_presentation_id: int,
    raw_material_id: int,
) -> BeerPresentationPackagingMaterial | None:
    return (
        db.query(BeerPresentationPackagingMaterial)
        .filter(
            BeerPresentationPackagingMaterial.beer_presentation_id
            == beer_presentation_id,
            BeerPresentationPackagingMaterial.raw_material_id
            == raw_material_id,
        )
        .first()
    )


def create_beer_presentation_packaging_material(
    db: Session,
    packaging_material_data: BeerPresentationPackagingMaterialCreate,
) -> BeerPresentationPackagingMaterial:
    packaging_material = BeerPresentationPackagingMaterial(
        **packaging_material_data.model_dump()
    )

    db.add(packaging_material)
    db.commit()
    db.refresh(packaging_material)

    return packaging_material