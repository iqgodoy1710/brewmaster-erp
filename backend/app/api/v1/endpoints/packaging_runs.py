from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.packaging_run import (
    PackagingRunCreate,
    PackagingRunResponse,
)
from app.services.packaging_run_service import PackagingRunService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/packaging-runs",
    tags=["Packaging Runs"],
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


@router.get("/", response_model=list[PackagingRunResponse])
def read_packaging_runs(
    db: Session = Depends(get_db),
):
    return PackagingRunService.get_all(db)


@router.post(
    "/",
    response_model=PackagingRunResponse,
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
def create_packaging_run(
    packaging_run: PackagingRunCreate,
    db: Session = Depends(get_db),
):
    return PackagingRunService.create(db, packaging_run)
