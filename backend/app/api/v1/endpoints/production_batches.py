from app.db.dependencies import get_db
from app.schemas.production_batch import (
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
    return ProductionBatchService.get_raw_material_planning_projection(
        db
    )

@router.post(
    "/",
    response_model=ProductionBatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_production_batch(
    production_batch: ProductionBatchCreate,
    db: Session = Depends(get_db),
):
    return ProductionBatchService.create(db, production_batch)