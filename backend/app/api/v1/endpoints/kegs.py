from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.keg import KegCreate, KegResponse
from app.schemas.keg_movement import (
    KegMovementResponse,
)
from app.services.keg_movement_service import (
    KegMovementService,
)
from app.services.keg_service import KegService
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/kegs",
    tags=["Kegs"],
)


@router.get(
    "/",
    response_model=list[KegResponse],
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
def read_kegs(
    db: Session = Depends(get_db),
):
    return KegService.get_all(db)


@router.post(
    "/",
    response_model=KegResponse,
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
def create_keg(
    keg: KegCreate,
    db: Session = Depends(get_db),
):
    return KegService.create(db, keg)


@router.get(
    "/{keg_id}/movements",
    response_model=list[KegMovementResponse],
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
def read_keg_movements(
    keg_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return KegMovementService.get_all_by_keg(
        db,
        keg_id,
    )
