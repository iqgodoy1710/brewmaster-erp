from app.common.exceptions import (
    BeerNotFoundError,
    InactiveBeerError,
    RecipeHasProductionBatchesError,
    RecipeNotFoundError,
    RecipeVersionAlreadyExistsError,
)
from app.crud.beer import get_beer_by_id
from app.crud.recipe import (
    create_recipe,
    get_recipe_by_beer_id_and_version,
    get_recipe_by_id,
    get_recipes,
    recipe_has_production_batches,
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
            raise InactiveBeerError(
                "Cannot create a recipe for an inactive beer."
            )

        existing_recipe = get_recipe_by_beer_id_and_version(
            db,
            recipe_data.beer_id,
            recipe_data.version,
        )
        if existing_recipe:
            raise RecipeVersionAlreadyExistsError(
                "A recipe with this beer and version already exists."
            )

        return create_recipe(db, recipe_data)

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