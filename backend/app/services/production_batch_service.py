from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.common.exceptions import (
    InactiveRecipeError,
    ProductionBatchCodeAlreadyExistsError,
    RecipeHasNoIngredientsError,
    RecipeNotFoundError,
)
from app.crud.production_batch import (
    create_production_batch,
    get_planned_production_batch_requirements,
    get_production_batch_by_code,
    get_production_batches,
)
from app.crud.recipe import get_recipe_by_id
from app.crud.recipe_ingredient import get_recipe_ingredients
from app.schemas.production_batch import ProductionBatchCreate
from app.schemas.production_planning import (
    RawMaterialPlanningProjectionResponse,
)


class ProductionBatchService:
    @staticmethod
    def get_all(db: Session):
        return get_production_batches(db)

    @staticmethod
    def create(
        db: Session,
        production_batch_data: ProductionBatchCreate,
    ):
        recipe = get_recipe_by_id(
            db,
            production_batch_data.recipe_id,
        )
        if not recipe:
            raise RecipeNotFoundError("The recipe does not exist.")

        if not recipe.active:
            raise InactiveRecipeError(
                "Cannot plan a production batch for an inactive recipe."
            )

        recipe_ingredients = get_recipe_ingredients(
            db,
            recipe.id,
        )
        if not recipe_ingredients:
            raise RecipeHasNoIngredientsError(
                "Cannot plan a production batch for a recipe without ingredients."
            )

        existing_production_batch = get_production_batch_by_code(
            db,
            production_batch_data.code,
        )
        if existing_production_batch:
            raise ProductionBatchCodeAlreadyExistsError(
                "A production batch with this code already exists."
            )

        return create_production_batch(db, production_batch_data)

    @staticmethod
    def get_raw_material_planning_projection(
        db: Session,
    ) -> list[RawMaterialPlanningProjectionResponse]:
        rows = get_planned_production_batch_requirements(db)

        projections: dict[int, dict] = {}

        for (
            production_batch,
            recipe,
            recipe_ingredient,
            raw_material,
            unit,
        ) in rows:
            planned_consumption = (
                recipe_ingredient.required_quantity
                * production_batch.planned_volume_liters
                / recipe.target_volume_liters
            )

            if raw_material.id not in projections:
                projections[raw_material.id] = {
                    "raw_material_id": raw_material.id,
                    "raw_material_code": raw_material.code,
                    "raw_material_name": raw_material.name,
                    "unit_symbol": unit.symbol,
                    "current_stock": raw_material.current_stock,
                    "planned_consumption": Decimal("0"),
                }

            projections[raw_material.id][
                "planned_consumption"
            ] += planned_consumption

        precision = Decimal("0.001")
        response = []

        for projection in projections.values():
            planned_consumption = projection[
                "planned_consumption"
            ].quantize(
                precision,
                rounding=ROUND_HALF_UP,
            )
            projected_available_stock = (
                projection["current_stock"] - planned_consumption
            ).quantize(
                precision,
                rounding=ROUND_HALF_UP,
            )

            response.append(
                RawMaterialPlanningProjectionResponse(
                    raw_material_id=projection["raw_material_id"],
                    raw_material_code=projection["raw_material_code"],
                    raw_material_name=projection["raw_material_name"],
                    unit_symbol=projection["unit_symbol"],
                    current_stock=projection["current_stock"],
                    planned_consumption=planned_consumption,
                    projected_available_stock=projected_available_stock,
                    has_shortage=projected_available_stock < 0,
                )
            )

        return sorted(
            response,
            key=lambda projection: projection.raw_material_name,
        )