from app.api.auth_dependencies import (
    get_current_user,
    require_authenticated_roles,
)
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[
        Depends(
            require_authenticated_roles(
                UserRole.ADMIN,
            )
        )
    ],
)


@router.get(
    "/",
    response_model=list[UserResponse],
)
def read_users(
    db: Session = Depends(get_db),
):
    return UserService.get_all(db)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    return UserService.create(db, user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int = Path(..., gt=0),
    user_data: UserUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserService.update(
        db,
        user_id,
        user_data,
        current_user,
    )
