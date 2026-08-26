from app.common.exceptions import (
    InactiveRawMaterialError,
    InactiveRecipeError,
    RawMaterialNotFoundError,
    RecipeIngredientAlreadyExistsError,
    RecipeIngredientNotFoundError,
    RecipeNotFoundError,
)
from app.crud.raw_material import get_raw_material_by_id
from app.crud.recipe import get_recipe_by_id
from app.crud.recipe_ingredient import (
    create_recipe_ingredient,
    deactivate_recipe_ingredient,
    get_recipe_ingredient_by_id,
    get_recipe_ingredient_by_recipe_id_and_raw_material_id,
    get_recipe_ingredients,
    reactivate_recipe_ingredient,
    replace_with_inactive_recipe_ingredient,
    update_recipe_ingredient,
)
from app.schemas.recipe_ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
)
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

        if existing_ingredient and existing_ingredient.active:
            raise RecipeIngredientAlreadyExistsError(
                "This raw material is already an ingredient of the recipe."
            )

        if existing_ingredient:
            return reactivate_recipe_ingredient(
                db,
                existing_ingredient,
                ingredient_data.required_quantity,
            )

        return create_recipe_ingredient(db, ingredient_data)

    @staticmethod
    def update(
        db: Session,
        ingredient_id: int,
        ingredient_data: RecipeIngredientUpdate,
    ):
        ingredient = get_recipe_ingredient_by_id(db, ingredient_id)
        if not ingredient or not ingredient.active:
            raise RecipeIngredientNotFoundError(
                "The recipe ingredient does not exist."
            )

        recipe = get_recipe_by_id(db, ingredient.recipe_id)
        if not recipe:
            raise RecipeNotFoundError("The recipe does not exist.")

        if not recipe.active:
            raise InactiveRecipeError(
                "Cannot modify ingredients of an inactive recipe."
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
                ingredient.recipe_id,
                ingredient_data.raw_material_id,
            )
        )

        if (
            existing_ingredient
            and existing_ingredient.id != ingredient.id
            and existing_ingredient.active
        ):
            raise RecipeIngredientAlreadyExistsError(
                "This raw material is already an ingredient of the recipe."
            )

        if existing_ingredient and existing_ingredient.id != ingredient.id:
            return replace_with_inactive_recipe_ingredient(
                db,
                ingredient,
                existing_ingredient,
                ingredient_data,
            )

        return update_recipe_ingredient(
            db,
            ingredient,
            ingredient_data,
        )

    @staticmethod
    def deactivate(
        db: Session,
        ingredient_id: int,
    ):
        ingredient = get_recipe_ingredient_by_id(db, ingredient_id)
        if not ingredient or not ingredient.active:
            raise RecipeIngredientNotFoundError(
                "The recipe ingredient does not exist."
            )

        return deactivate_recipe_ingredient(db, ingredient)