from typing import List

import app.models
from app.db.dependencies import get_db
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get(
    "/",
    response_model=List[CategoryResponse]
)
def read_categories(db: Session = Depends(get_db)):
    return CategoryService.get_all(db)

@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
):
    return CategoryService.create(db, category)
