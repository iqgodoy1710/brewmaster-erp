from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.beer_presentation_price import (
    BeerPresentationPriceCreate,
    BeerPresentationPriceResponse,
)
from app.services.beer_presentation_price_service import (
    BeerPresentationPriceService,
)


router = APIRouter(
    tags=["Beer Presentation Prices"],
)


@router.get(
    "/beer-presentations/{beer_presentation_id}/prices",
    response_model=list[BeerPresentationPriceResponse],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)
def read_beer_presentation_prices(
    beer_presentation_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return BeerPresentationPriceService.get_all_by_beer_presentation(
        db,
        beer_presentation_id,
    )


@router.post(
    "/beer-presentation-prices/",
    response_model=BeerPresentationPriceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)
def create_beer_presentation_price(
    price: BeerPresentationPriceCreate,
    db: Session = Depends(get_db),
):
    return BeerPresentationPriceService.create(db, price)