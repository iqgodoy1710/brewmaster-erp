from app.db.dependencies import get_db
from app.schemas.recipe import RecipeCreate, RecipeResponse
from app.services.recipe_service import RecipeService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get("/", response_model=list[RecipeResponse])
def read_recipes(db: Session = Depends(get_db)):
    return RecipeService.get_all(db)


@router.post(
    "/",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
):
    return RecipeService.create(db, recipe)