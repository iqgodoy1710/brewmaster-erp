from app.db.dependencies import get_db
from app.schemas.beer_presentation import (
    BeerPresentationCreate,
    BeerPresentationMinimumStockUpdate,
    BeerPresentationResponse,
)
from app.schemas.inventory_alert import (
    BeerPresentationLowStockResponse,
)
from app.services.beer_presentation_service import BeerPresentationService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/beer-presentations",
    tags=["Beer Presentations"],
)


@router.get("/", response_model=list[BeerPresentationResponse])
def read_beer_presentations(
    db: Session = Depends(get_db),
):
    return BeerPresentationService.get_all(db)

@router.get(
    "/low-stock",
    response_model=list[BeerPresentationLowStockResponse],
)
def read_beer_presentation_low_stock_alerts(
    db: Session = Depends(get_db),
):
    return BeerPresentationService.get_low_stock_alerts(db)


@router.post(
    "/",
    response_model=BeerPresentationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_beer_presentation(
    presentation: BeerPresentationCreate,
    db: Session = Depends(get_db),
):
    return BeerPresentationService.create(db, presentation)

@router.patch(
    "/{code}/minimum-stock",
    response_model=BeerPresentationResponse,
)
def update_beer_presentation_minimum_stock(
    code: str,
    minimum_stock_data: BeerPresentationMinimumStockUpdate,
    db: Session = Depends(get_db),
):
    return BeerPresentationService.update_minimum_stock(
        db,
        code,
        minimum_stock_data,
    )