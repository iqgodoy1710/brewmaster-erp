from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.bottle_pasteurization_run import (
    BottlePasteurizationRunCreate,
    BottlePasteurizationRunResponse,
)
from app.services.bottle_pasteurization_run_service import (
    BottlePasteurizationRunService,
)
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/bottle-pasteurization-runs",
    tags=["Bottle Pasteurization Runs"],
)


@router.get(
    "/",
    response_model=list[BottlePasteurizationRunResponse],
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
def read_bottle_pasteurization_runs(
    db: Session = Depends(get_db),
):
    return BottlePasteurizationRunService.get_all(db)


@router.post(
    "/",
    response_model=BottlePasteurizationRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_bottle_pasteurization_run(
    pasteurization_data: BottlePasteurizationRunCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
        )
    ),
):
    return BottlePasteurizationRunService.create(
        db,
        pasteurization_data,
        current_user,
    )