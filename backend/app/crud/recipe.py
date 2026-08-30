from app.models.production_batch import ProductionBatch
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeUpdate
from sqlalchemy.orm import Session


def get_recipes(db: Session) -> list[Recipe]:
    return db.query(Recipe).filter(Recipe.active.is_(True)).all()


def get_recipe_by_beer_id_and_version(
    db: Session,
    beer_id: int,
    version: int,
) -> Recipe | None:
    return (
        db.query(Recipe)
        .filter(
            Recipe.beer_id == beer_id,
            Recipe.version == version,
        )
        .first()
    )


def create_recipe(
    db: Session,
    recipe_data: RecipeCreate,
) -> Recipe:
    recipe = Recipe(**recipe_data.model_dump())

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return recipe


def get_recipe_by_id(
    db: Session,
    recipe_id: int,
) -> Recipe | None:
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()


def recipe_has_production_batches(
    db: Session,
    recipe_id: int,
) -> bool:
    return (
        db.query(ProductionBatch.id)
        .filter(ProductionBatch.recipe_id == recipe_id)
        .first()
        is not None
    )


def update_recipe(
    db: Session,
    recipe: Recipe,
    recipe_data: RecipeUpdate,
) -> Recipe:
    update_data = recipe_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(recipe, field, value)

    db.commit()
    db.refresh(recipe)

    return recipe
