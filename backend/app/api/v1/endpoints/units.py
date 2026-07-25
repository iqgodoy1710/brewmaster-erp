import app.models
from app.db.dependencies import get_db
from app.schemas.unit import UnitCreate, UnitResponse
from app.services.unit_service import UnitService
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/units", tags=["Units"])


@router.get("/", response_model=list[UnitResponse])
def read_units(db: Session = Depends(get_db)):
    return UnitService.get_all(db)


@router.post("/", response_model=UnitResponse)
def create_unit(
    unit: UnitCreate,
    db: Session = Depends(get_db),
):
    return UnitService.create(db, unit)
