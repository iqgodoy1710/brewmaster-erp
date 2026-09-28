from app.common.exceptions import (
    BeerNotFoundError,
    InactiveBeerError,
    InactiveRecipeError,
    RecipeHasProductionBatchesError,
    RecipeNotFoundError,
    RecipeVersionAlreadyExistsError,
)
from app.crud.beer import get_beer_by_id
from app.crud.recipe import (
    clear_current_recipe,
    create_recipe,
    get_current_recipe_by_beer_id,
    get_recipe_by_beer_id_and_version,
    get_recipe_by_id,
    get_recipes,
    recipe_has_production_batches,
    set_recipe_as_current,
    update_recipe,
)
from app.schemas.recipe import RecipeCreate, RecipeUpdate
from sqlalchemy.orm import Session


class RecipeService:
    @staticmethod
    def get_all(db: Session):
        return get_recipes(db)

    @staticmethod
    def create(
        db: Session,
        recipe_data: RecipeCreate,
    ):
        beer = get_beer_by_id(db, recipe_data.beer_id)
        if not beer:
            raise BeerNotFoundError("The beer does not exist.")

        if not beer.active:
            raise InactiveBeerError("Cannot create a recipe for an inactive beer.")

        existing_recipe = get_recipe_by_beer_id_and_version(
            db,
            recipe_data.beer_id,
            recipe_data.version,
        )
        if existing_recipe:
            raise RecipeVersionAlreadyExistsError(
                "A recipe with this beer and version already exists."
            )

        current_recipe = get_current_recipe_by_beer_id(
            db,
            recipe_data.beer_id,
        )

        should_be_current = recipe_data.is_current or current_recipe is None

        normalized_recipe_data = recipe_data.model_copy(
            update={
                "is_current": should_be_current,
            }
        )

        try:
            if should_be_current:
                clear_current_recipe(
                    db,
                    recipe_data.beer_id,
                )

            recipe = create_recipe(
                db,
                normalized_recipe_data,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        db.refresh(recipe)

        return recipe

    @staticmethod
    def update(
        db: Session,
        recipe_id: int,
        recipe_data: RecipeUpdate,
    ):
        recipe = get_recipe_by_id(db, recipe_id)

        if not recipe:
            raise RecipeNotFoundError("The recipe does not exist.")

        if recipe_has_production_batches(db, recipe.id):
            raise RecipeHasProductionBatchesError(
                "A recipe with production batches cannot be modified. "
                "Create a new version instead."
            )

        return update_recipe(
            db,
            recipe,
            recipe_data,
        )

    @staticmethod
    def set_current(
        db: Session,
        recipe_id: int,
    ):
        recipe = get_recipe_by_id(
            db,
            recipe_id,
        )

        if not recipe:
            raise RecipeNotFoundError(
                "The recipe does not exist."
            )

        if not recipe.active:
            raise InactiveRecipeError(
                "An inactive recipe cannot be selected "
                "as the current recipe."
            )

        if recipe.is_current:
            return recipe

        try:
            set_recipe_as_current(
                db,
                recipe,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        db.refresh(recipe)

        return recipe