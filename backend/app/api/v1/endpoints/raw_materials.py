from typing import List

import app.models
from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.inventory_alert import RawMaterialLowStockResponse
from app.schemas.raw_material import (
    RawMaterialCreate,
    RawMaterialResponse,
    RawMaterialUpdate,
)
from app.schemas.raw_material_reference import RawMaterialReferenceResponse
from app.services.raw_material_service import RawMaterialService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/raw-materials", tags=["Raw Materials"])


@router.get(
    "/",
    response_model=List[RawMaterialResponse],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)
def read_raw_materials(
    db: Session = Depends(get_db),
):
    return RawMaterialService.get_all(db)


@router.post(
    "/",
    response_model=RawMaterialResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)
def create_raw_material(
    raw_material: RawMaterialCreate,
    db: Session = Depends(get_db),
):
    return RawMaterialService.create(db, raw_material)


@router.get(
    "/low-stock",
    response_model=list[RawMaterialLowStockResponse],
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
def read_raw_material_low_stock_alerts(
    db: Session = Depends(get_db),
):
    return RawMaterialService.get_low_stock_alerts(db)

@router.get(
    "/references",
    response_model=list[RawMaterialReferenceResponse],
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
def read_raw_material_references(
    db: Session = Depends(get_db),
):
    return RawMaterialService.get_references(db)

@router.get(
    "/{code}",
    response_model=RawMaterialResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)
def read_raw_material_by_code(
    code: str,
    db: Session = Depends(get_db),
):
    return RawMaterialService.get_by_code(db, code)


@router.patch(
    "/{code}",
    response_model=RawMaterialResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)
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


@router.delete(
    "/{code}",
    response_model=RawMaterialResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)
def deactivate_raw_material(
    code: str,
    db: Session = Depends(get_db),
):
    return RawMaterialService.deactivate(db, code)
