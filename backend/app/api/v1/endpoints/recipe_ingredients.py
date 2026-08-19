from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.recipe_ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientResponse,
)
from app.services.recipe_ingredient_service import RecipeIngredientService
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Recipe Ingredients"],
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


@router.get(
    "/recipes/{recipe_id}/ingredients",
    response_model=list[RecipeIngredientResponse],
)
def read_recipe_ingredients(
    recipe_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return RecipeIngredientService.get_all_by_recipe(db, recipe_id)


@router.post(
    "/recipe-ingredients/",
    response_model=RecipeIngredientResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
            )
        )
    ],
)
def create_recipe_ingredient(
    ingredient: RecipeIngredientCreate,
    db: Session = Depends(get_db),
):
    return RecipeIngredientService.create(db, ingredient)
