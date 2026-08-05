from app.db.dependencies import get_db
from app.schemas.beer_presentation_packaging_material import (
    BeerPresentationPackagingMaterialCreate,
    BeerPresentationPackagingMaterialResponse,
)
from app.services.beer_presentation_packaging_material_service import (
    BeerPresentationPackagingMaterialService,
)
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Beer Presentation Packaging Materials"],
)


@router.get(
    "/beer-presentations/{beer_presentation_id}/packaging-materials",
    response_model=list[BeerPresentationPackagingMaterialResponse],
)
def read_beer_presentation_packaging_materials(
    beer_presentation_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return BeerPresentationPackagingMaterialService.get_all_by_beer_presentation(
        db,
        beer_presentation_id,
    )


@router.post(
    "/beer-presentation-packaging-materials/",
    response_model=BeerPresentationPackagingMaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_beer_presentation_packaging_material(
    packaging_material: BeerPresentationPackagingMaterialCreate,
    db: Session = Depends(get_db),
):
    return BeerPresentationPackagingMaterialService.create(
        db,
        packaging_material,
    )