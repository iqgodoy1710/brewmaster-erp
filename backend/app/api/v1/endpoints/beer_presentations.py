from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.beer_presentation import (
    BeerPresentationCreate,
    BeerPresentationResponse,
)
from app.services.beer_presentation_service import BeerPresentationService


router = APIRouter(
    prefix="/beer-presentations",
    tags=["Beer Presentations"],
)


@router.get("/", response_model=list[BeerPresentationResponse])
def read_beer_presentations(
    db: Session = Depends(get_db),
):
    return BeerPresentationService.get_all(db)


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