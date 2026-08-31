from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.production_batch import (
    ProductionBatchComplete,
    ProductionBatchCreate,
    ProductionBatchResponse,
)
from app.schemas.production_planning import (
    RawMaterialPlanningProjectionResponse,
)
from app.services.production_batch_service import ProductionBatchService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/production-batches",
    tags=["Production Batches"],
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


@router.get("/", response_model=list[ProductionBatchResponse])
def read_production_batches(
    db: Session = Depends(get_db),
):
    return ProductionBatchService.get_all(db)


@router.get(
    "/planning/raw-material-requirements",
    response_model=list[RawMaterialPlanningProjectionResponse],
)
def read_raw_material_planning_projection(
    db: Session = Depends(get_db),
):
    return ProductionBatchService.get_raw_material_planning_projection(db)


@router.post(
    "/",
    response_model=ProductionBatchResponse,
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
def create_production_batch(
    production_batch: ProductionBatchCreate,
    db: Session = Depends(get_db),
):
    return ProductionBatchService.create(db, production_batch)


@router.post(
    "/{code:path}/start",
    response_model=ProductionBatchResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.OPERATOR,
            )
        )
    ],
)
def start_production_batch(
    code: str,
    db: Session = Depends(get_db),
):
    return ProductionBatchService.start(db, code)


@router.post(
    "/{code:path}/cancel",
    response_model=ProductionBatchResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.OPERATOR,
            )
        )
    ],
)
def cancel_production_batch(
    code: str,
    db: Session = Depends(get_db),
):
    return ProductionBatchService.cancel(db, code)


@router.post(
    "/{code:path}/complete",
    response_model=ProductionBatchResponse,
)
def complete_production_batch(
    code: str,
    completion: ProductionBatchComplete,
    db: Session = Depends(get_db),
):
    return ProductionBatchService.complete(
        db,
        code,
        completion,
    )
