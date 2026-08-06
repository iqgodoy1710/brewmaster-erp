from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.packaging_run import (
    PackagingRunCreate,
    PackagingRunResponse,
)
from app.services.packaging_run_service import PackagingRunService


router = APIRouter(
    prefix="/packaging-runs",
    tags=["Packaging Runs"],
)


@router.get("/", response_model=list[PackagingRunResponse])
def read_packaging_runs(
    db: Session = Depends(get_db),
):
    return PackagingRunService.get_all(db)


@router.post(
    "/",
    response_model=PackagingRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_packaging_run(
    packaging_run: PackagingRunCreate,
    db: Session = Depends(get_db),
):
    return PackagingRunService.create(db, packaging_run)