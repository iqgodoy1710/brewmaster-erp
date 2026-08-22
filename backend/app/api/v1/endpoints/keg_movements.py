from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.keg_movement import (
    KegFillCreate,
    KegMovementResponse,
    KegRemnantTransferCreate,
    KegRemnantTransferResponse,
    KegReturnCreate,
    KegWashCreate,
)
from app.services.keg_movement_service import (
    KegMovementService,
)
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Keg Movements"],
)


@router.post(
    "/keg-movements/fill",
    response_model=KegMovementResponse,
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
def fill_keg(
    filling_data: KegFillCreate,
    db: Session = Depends(get_db),
):
    return KegMovementService.fill(
        db,
        filling_data,
    )

@router.post(
    "/keg-movements/return",
    response_model=KegMovementResponse,
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
def return_keg(
    return_data: KegReturnCreate,
    db: Session = Depends(get_db),
):
    return KegMovementService.return_keg(
        db,
        return_data,
    )

@router.post(
    "/keg-movements/wash",
    response_model=KegMovementResponse,
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
def wash_keg(
    washing_data: KegWashCreate,
    db: Session = Depends(get_db),
):
    return KegMovementService.wash(
        db,
        washing_data,
    )

@router.post(
    "/keg-movements/transfer-remnants",
    response_model=KegRemnantTransferResponse,
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
def transfer_keg_remnants(
    transfer_data: KegRemnantTransferCreate,
    db: Session = Depends(get_db),
):
    return KegMovementService.transfer_remnants(
        db,
        transfer_data,
    )