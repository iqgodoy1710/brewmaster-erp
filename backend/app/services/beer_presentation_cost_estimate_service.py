from decimal import Decimal

from app.common.exceptions import (
    BeerPresentationNotFoundError,
    InvalidBeerPresentationCostEstimateError,
    RecipeHasNoIngredientsError,
    RecipeNotFoundError,
)
from app.crud.beer_presentation import get_beer_presentation_by_id
from app.crud.beer_presentation_packaging_material import (
    get_beer_presentation_packaging_materials,
)
from app.crud.raw_material import get_raw_material_by_id
from app.crud.recipe import get_recipe_by_id
from app.crud.recipe_ingredient import get_recipe_ingredients
from app.crud.unit import get_unit_by_id
from app.schemas.beer_presentation_cost_estimate import (
    BeerPresentationCostComponentResponse,
    BeerPresentationCostEstimateResponse,
)
from sqlalchemy.orm import Session


class BeerPresentationCostEstimateService:
    @staticmethod
    def get_estimate(
        db: Session,
        beer_presentation_id: int,
        recipe_id: int,
    ) -> BeerPresentationCostEstimateResponse:
        beer_presentation = get_beer_presentation_by_id(
            db,
            beer_presentation_id,
        )
        if not beer_presentation:
            raise BeerPresentationNotFoundError(
                "The beer presentation does not exist."
            )

        recipe = get_recipe_by_id(db, recipe_id)
        if not recipe:
            raise RecipeNotFoundError("The recipe does not exist.")

        if recipe.beer_id != beer_presentation.beer_id:
            raise InvalidBeerPresentationCostEstimateError(
                "The recipe does not belong to the beer presentation beer."
            )

        recipe_ingredients = get_recipe_ingredients(db, recipe.id)
        if not recipe_ingredients:
            raise RecipeHasNoIngredientsError(
                "The selected recipe does not have ingredients."
            )

        packaging_volume_liters = (
            beer_presentation.packaging_format.capacity_liters
        )

        components: list[BeerPresentationCostComponentResponse] = []
        beer_cost = Decimal("0")
        packaging_material_cost = Decimal("0")

        for ingredient in recipe_ingredients:
            raw_material = get_raw_material_by_id(
                db,
                ingredient.raw_material_id,
            )
            unit = get_unit_by_id(db, raw_material.unit_id)

            quantity = (
                ingredient.required_quantity
                * packaging_volume_liters
                / recipe.target_volume_liters
            )
            subtotal = quantity * raw_material.current_cost

            beer_cost += subtotal

            components.append(
                BeerPresentationCostComponentResponse(
                    component_type="beer",
                    raw_material_id=raw_material.id,
                    raw_material_code=raw_material.code,
                    raw_material_name=raw_material.name,
                    unit_symbol=unit.symbol,
                    quantity=quantity,
                    unit_cost=raw_material.current_cost,
                    subtotal=subtotal,
                )
            )

        packaging_materials = (
            get_beer_presentation_packaging_materials(
                db,
                beer_presentation.id,
            )
        )

        for packaging_material in packaging_materials:
            raw_material = get_raw_material_by_id(
                db,
                packaging_material.raw_material_id,
            )
            unit = get_unit_by_id(db, raw_material.unit_id)

            quantity = packaging_material.required_quantity
            subtotal = quantity * raw_material.current_cost

            packaging_material_cost += subtotal

            components.append(
                BeerPresentationCostComponentResponse(
                    component_type="packaging",
                    raw_material_id=raw_material.id,
                    raw_material_code=raw_material.code,
                    raw_material_name=raw_material.name,
                    unit_symbol=unit.symbol,
                    quantity=quantity,
                    unit_cost=raw_material.current_cost,
                    subtotal=subtotal,
                )
            )

        return BeerPresentationCostEstimateResponse(
            beer_presentation_id=beer_presentation.id,
            beer_presentation_code=beer_presentation.code,
            beer_presentation_name=beer_presentation.name,
            packaging_volume_liters=packaging_volume_liters,
            recipe_id=recipe.id,
            recipe_version=recipe.version,
            recipe_target_volume_liters=recipe.target_volume_liters,
            beer_cost=beer_cost,
            packaging_material_cost=packaging_material_cost,
            total_unit_cost=beer_cost + packaging_material_cost,
            components=components,
        )