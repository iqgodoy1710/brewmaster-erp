from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.recipe import (
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
)
from app.services.recipe_service import RecipeService
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
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


@router.get("/", response_model=list[RecipeResponse])
def read_recipes(db: Session = Depends(get_db)):
    return RecipeService.get_all(db)


@router.post(
    "/",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
            )
        )
    ],
)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
):
    return RecipeService.create(db, recipe)

@router.patch(
    "/{recipe_id}",
    response_model=RecipeResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
            )
        )
    ],
)
def update_recipe(
    recipe_data: RecipeUpdate,
    recipe_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return RecipeService.update(
        db,
        recipe_id,
        recipe_data,
    )