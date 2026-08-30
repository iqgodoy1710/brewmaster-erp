from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.keg_repackaging_run import (
    KegRepackagingRunCreate,
    KegRepackagingRunResponse,
)
from app.services.keg_repackaging_run_service import (
    KegRepackagingRunService,
)
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/keg-repackaging-runs",
    tags=["Keg Repackaging Runs"],
)


@router.get(
    "/",
    response_model=list[KegRepackagingRunResponse],
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
def read_keg_repackaging_runs(
    db: Session = Depends(get_db),
):
    return KegRepackagingRunService.get_all(db)


@router.post(
    "/",
    response_model=KegRepackagingRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_keg_repackaging_run(
    repackaging_run: KegRepackagingRunCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
        )
    ),
):
    return KegRepackagingRunService.create(
        db,
        repackaging_run,
        performed_by_user_id=(
            current_user.id if current_user else None
        ),
    )