from app.db.dependencies import get_db
from app.schemas.raw_material_stock_movement import (
    RawMaterialStockMovementCreate,
    RawMaterialStockMovementResponse,
)
from app.services.raw_material_stock_movement_service import (
    RawMaterialStockMovementService,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/raw-material-stock-movements",
    tags=["Raw Material Stock Movements"],
)


@router.post("/", response_model=RawMaterialStockMovementResponse)
def create_raw_material_stock_movement(
    movement: RawMaterialStockMovementCreate,
    db: Session = Depends(get_db),
):
    return RawMaterialStockMovementService.create(db, movement)

@router.get(
    "/{raw_material_id}",
    response_model=list[RawMaterialStockMovementResponse],
)
def read_raw_material_stock_movements(
    raw_material_id: int,
    db: Session = Depends(get_db),
):
    return RawMaterialStockMovementService.get_all_by_raw_material(
        db,
        raw_material_id,
    )