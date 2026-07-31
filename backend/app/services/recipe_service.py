from app.common.exceptions import (
    BeerNotFoundError,
    InactiveBeerError,
    RecipeVersionAlreadyExistsError,
)
from app.crud.beer import get_beer_by_id
from app.crud.recipe import (
    create_recipe,
    get_recipe_by_beer_id_and_version,
    get_recipes,
)
from app.schemas.recipe import RecipeCreate
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