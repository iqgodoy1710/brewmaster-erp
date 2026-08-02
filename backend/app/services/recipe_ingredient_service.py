from app.common.exceptions import (
    InactiveRawMaterialError,
    InactiveRecipeError,
    RawMaterialNotFoundError,
    RecipeIngredientAlreadyExistsError,
    RecipeNotFoundError,
)
from app.crud.raw_material import get_raw_material_by_id
from app.crud.recipe import get_recipe_by_id
from app.crud.recipe_ingredient import (
    create_recipe_ingredient,
    get_recipe_ingredient_by_recipe_id_and_raw_material_id,
    get_recipe_ingredients,
)
from app.schemas.recipe_ingredient import RecipeIngredientCreate
from sqlalchemy.orm import Session


class RecipeIngredientService:
    @staticmethod
    def get_all_by_recipe(
        db: Session,
        recipe_id: int,
    ):
        recipe = get_recipe_by_id(db, recipe_id)
        if not recipe:
            raise RecipeNotFoundError("The recipe does not exist.")

        return get_recipe_ingredients(db, recipe_id)

    @staticmethod
    def create(
        db: Session,
        ingredient_data: RecipeIngredientCreate,
    ):
        recipe = get_recipe_by_id(db, ingredient_data.recipe_id)
        if not recipe:
            raise RecipeNotFoundError("The recipe does not exist.")

        if not recipe.active:
            raise InactiveRecipeError(
                "Cannot add ingredients to an inactive recipe."
            )

        raw_material = get_raw_material_by_id(
            db,
            ingredient_data.raw_material_id,
        )
        if not raw_material:
            raise RawMaterialNotFoundError(
                "The raw material does not exist."
            )

        if not raw_material.active:
            raise InactiveRawMaterialError(
                "Cannot add an inactive raw material to a recipe."
            )

        existing_ingredient = (
            get_recipe_ingredient_by_recipe_id_and_raw_material_id(
                db,
                ingredient_data.recipe_id,
                ingredient_data.raw_material_id,
            )
        )
        if existing_ingredient:
            raise RecipeIngredientAlreadyExistsError(
                "This raw material is already an ingredient of the recipe."
            )

        return create_recipe_ingredient(db, ingredient_data)