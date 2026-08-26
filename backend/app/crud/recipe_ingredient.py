from sqlalchemy.orm import Session

from app.models.recipe_ingredient import RecipeIngredient
from app.schemas.recipe_ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
)


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


def get_recipe_ingredient_by_id(
    db: Session,
    ingredient_id: int,
) -> RecipeIngredient | None:
    return (
        db.query(RecipeIngredient)
        .filter(RecipeIngredient.id == ingredient_id)
        .first()
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


def reactivate_recipe_ingredient(
    db: Session,
    ingredient: RecipeIngredient,
    required_quantity,
) -> RecipeIngredient:
    ingredient.required_quantity = required_quantity
    ingredient.active = True

    db.commit()
    db.refresh(ingredient)

    return ingredient


def update_recipe_ingredient(
    db: Session,
    ingredient: RecipeIngredient,
    ingredient_data: RecipeIngredientUpdate,
) -> RecipeIngredient:
    ingredient.raw_material_id = ingredient_data.raw_material_id
    ingredient.required_quantity = ingredient_data.required_quantity

    db.commit()
    db.refresh(ingredient)

    return ingredient


def replace_with_inactive_recipe_ingredient(
    db: Session,
    current_ingredient: RecipeIngredient,
    inactive_ingredient: RecipeIngredient,
    ingredient_data: RecipeIngredientUpdate,
) -> RecipeIngredient:
    current_ingredient.active = False
    inactive_ingredient.active = True
    inactive_ingredient.required_quantity = ingredient_data.required_quantity

    db.commit()
    db.refresh(inactive_ingredient)

    return inactive_ingredient


def deactivate_recipe_ingredient(
    db: Session,
    ingredient: RecipeIngredient,
) -> RecipeIngredient:
    ingredient.active = False

    db.commit()
    db.refresh(ingredient)

    return ingredient