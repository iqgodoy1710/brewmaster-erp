from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.beer import (
    BeerCreate,
    BeerMinimumStockUpdate,
    BeerResponse,
)
from app.services.beer_service import BeerService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/beers", tags=["Beers"])


@router.get(
    "/",
    response_model=list[BeerResponse],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
                UserRole.OPERATOR,
            )
        )
    ],
)
def read_beers(db: Session = Depends(get_db)):
    return BeerService.get_all(db)


@router.post(
    "/",
    response_model=BeerResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_roles(UserRole.ADMIN))
    ],
)
def create_beer(
    beer: BeerCreate,
    db: Session = Depends(get_db),
):
    return BeerService.create(db, beer)


@router.patch(
    "/{code}/minimum-stock",
    response_model=BeerResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)
def update_beer_minimum_stock(
    code: str,
    minimum_stock_data: BeerMinimumStockUpdate,
    db: Session = Depends(get_db),
):
    return BeerService.update_minimum_stock(
        db,
        code,
        minimum_stock_data,
    )