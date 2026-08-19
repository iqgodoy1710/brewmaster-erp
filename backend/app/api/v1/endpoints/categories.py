from typing import List

import app.models
from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
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


@router.get("/", response_model=List[CategoryResponse])
def read_categories(db: Session = Depends(get_db)):
    return CategoryService.get_all(db)


@router.post(
    "/",
    response_model=CategoryResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
            )
        )
    ],
)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
):
    return CategoryService.create(db, category)
