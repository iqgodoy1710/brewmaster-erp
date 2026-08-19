from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.beer_presentation_stock_movement import (
    BeerPresentationStockMovementCreate,
    BeerPresentationStockMovementResponse,
)
from app.services.beer_presentation_stock_movement_service import (
    BeerPresentationStockMovementService,
)
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Beer Presentation Stock Movements"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.OPERATOR,
                UserRole.MANAGEMENT,
            )
        )
    ],
)


@router.get(
    "/beer-presentations/{beer_presentation_id}/stock-movements",
    response_model=list[BeerPresentationStockMovementResponse],
)
def read_beer_presentation_stock_movements(
    beer_presentation_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return BeerPresentationStockMovementService.get_all_by_beer_presentation(
        db,
        beer_presentation_id,
    )


@router.post(
    "/beer-presentation-stock-movements/",
    response_model=BeerPresentationStockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.OPERATOR,
            )
        )
    ],
)
def create_beer_presentation_stock_movement(
    movement: BeerPresentationStockMovementCreate,
    db: Session = Depends(get_db),
):
    return BeerPresentationStockMovementService.create(
        db,
        movement,
    )
