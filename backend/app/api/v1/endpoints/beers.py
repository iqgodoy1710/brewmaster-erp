
from app.db.dependencies import get_db
from app.schemas.beer import BeerCreate, BeerResponse
from app.services.beer_service import BeerService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/beers", tags=["Beers"])


@router.get("/", response_model=list[BeerResponse])
def read_beers(db: Session = Depends(get_db)):
    return BeerService.get_all(db)


@router.post("/", response_model=BeerResponse, status_code=status.HTTP_201_CREATED,)
def create_beer(
    beer: BeerCreate,
    db: Session = Depends(get_db),
):
    return BeerService.create(db, beer)
