from app.models.recipe_ingredient import RecipeIngredient
from app.schemas.recipe_ingredient import RecipeIngredientCreate
from sqlalchemy.orm import Session


def get_recipe_ingredients(
    db: Session,
    recipe_id: int,
) -> list[RecipeIngredient]:
    return (
        db.query(RecipeIngredient)
        .filter(
            RecipeIngredient.recipe_id == recipe_id,
            RecipeIngredient.active.is_(True),
        )
        .all()
    )


def get_recipe_ingredient_by_recipe_id_and_raw_material_id(
    db: Session,
    recipe_id: int,
    raw_material_id: int,
) -> RecipeIngredient | None:
    return (
        db.query(RecipeIngredient)
        .filter(
            RecipeIngredient.recipe_id == recipe_id,
            RecipeIngredient.raw_material_id == raw_material_id,
        )
        .first()
    )


def create_recipe_ingredient(
    db: Session,
    ingredient_data: RecipeIngredientCreate,
) -> RecipeIngredient:
    ingredient = RecipeIngredient(**ingredient_data.model_dump())

    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    return ingredient