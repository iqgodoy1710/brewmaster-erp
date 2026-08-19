from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.raw_material_stock_movement import (
    RawMaterialStockMovementCreate,
    RawMaterialStockMovementResponse,
)
from app.services.raw_material_stock_movement_service import (
    RawMaterialStockMovementService,
)
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/raw-material-stock-movements",
    tags=["Raw Material Stock Movements"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)


@router.post(
    "/",
    response_model=RawMaterialStockMovementResponse,
    status_code=status.HTTP_201_CREATED,
)
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
