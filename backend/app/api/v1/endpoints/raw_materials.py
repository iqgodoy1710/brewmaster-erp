import app.models
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session


from app.db.dependencies import get_db
from app.schemas.raw_material import (
    RawMaterialResponse,
    RawMaterialCreate,
    RawMaterialUpdate,
)
from app.services.raw_material_service import RawMaterialService


router = APIRouter(prefix="/raw-materials", tags=["Raw Materials"])


@router.get("/", response_model=List[RawMaterialResponse])
def read_raw_materials(db: Session = Depends(get_db)):
    return RawMaterialService.get_all(db)


@router.post(
    "/",
    response_model=RawMaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_raw_material(
    raw_material: RawMaterialCreate,
    db: Session = Depends(get_db),
):
    return RawMaterialService.create(db, raw_material)


@router.get("/{code}", response_model=RawMaterialResponse)
def read_raw_material_by_code(
    code: str,
    db: Session = Depends(get_db),
):
    return RawMaterialService.get_by_code(db, code)


@router.patch("/{code}", response_model=RawMaterialResponse)
def update_raw_material(
    code: str,
    raw_material: RawMaterialUpdate,
    db: Session = Depends(get_db),
):
    return RawMaterialService.update(
        db,
        code,
        raw_material,
    )


@router.delete("/{code}", response_model=RawMaterialResponse)
def deactivate_raw_material(
    code: str,
    db: Session = Depends(get_db),
):
    return RawMaterialService.deactivate(db, code)
