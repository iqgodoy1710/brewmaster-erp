from decimal import ROUND_HALF_UP, Decimal

from app.common.exceptions import (
    InactiveRawMaterialError,
    InactiveRecipeError,
    InsufficientStockError,
    InvalidProductionBatchStatusError,
    ProductionBatchCodeAlreadyExistsError,
    ProductionBatchNotFoundError,
    RawMaterialNotFoundError,
    RecipeHasNoIngredientsError,
    RecipeNotFoundError,
)
from app.crud.production_batch import (
    complete_production_batch,
    create_production_batch,
    get_planned_production_batch_requirements,
    get_production_batch_by_code,
    get_production_batches,
)
from app.crud.raw_material import (
    get_raw_material_by_id,
    update_raw_material_stock,
)
from app.crud.raw_material_stock_movement import (
    create_production_consumption_movement,
)
from app.crud.recipe import get_recipe_by_id
from app.crud.recipe_ingredient import get_recipe_ingredients
from app.models.enums import ProductionBatchStatus
from app.schemas.production_batch import ProductionBatchComplete, ProductionBatchCreate
from app.schemas.production_planning import (
    RawMaterialPlanningProjectionResponse,
)
from sqlalchemy.orm import Session


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
    def complete(
        db: Session,
        code: str,
        completion_data: ProductionBatchComplete,
    ):
        production_batch = get_production_batch_by_code(db, code)
        if not production_batch:
            raise ProductionBatchNotFoundError("The production batch does not exist.")

        if not production_batch.active:
            raise InvalidProductionBatchStatusError(
                "Cannot complete an inactive production batch."
            )

        if production_batch.status != ProductionBatchStatus.PLANNED:
            raise InvalidProductionBatchStatusError(
                "Only planned production batches can be completed."
            )

        recipe_ingredients = get_recipe_ingredients(
            db,
            production_batch.recipe_id,
        )
        if not recipe_ingredients:
            raise RecipeHasNoIngredientsError(
                "Cannot complete a production batch for a recipe without ingredients."
            )

        consumptions = []

        for recipe_ingredient in recipe_ingredients:
            raw_material = get_raw_material_by_id(
                db,
                recipe_ingredient.raw_material_id,
            )
            if not raw_material:
                raise RawMaterialNotFoundError("The raw material does not exist.")

            if not raw_material.active:
                raise InactiveRawMaterialError(
                    "Cannot consume an inactive raw material."
                )

            quantity = ProductionBatchService._calculate_recipe_ingredient_consumption(
                recipe_ingredient.required_quantity,
                production_batch.planned_volume_liters,
                production_batch.recipe.target_volume_liters,
            )

            if raw_material.current_stock < quantity:
                raise InsufficientStockError(
                    f"Insufficient stock for raw material: {raw_material.name}."
                )

            consumptions.append((raw_material, quantity))

        try:
            for raw_material, quantity in consumptions:
                create_production_consumption_movement(
                    db,
                    raw_material_id=raw_material.id,
                    production_batch_id=production_batch.id,
                    quantity=quantity,
                    reference=production_batch.code,
                    notes=(
                        "Automatically generated when completing a production batch."
                    ),
                )
                update_raw_material_stock(
                    db,
                    raw_material,
                    raw_material.current_stock - quantity,
                )

            complete_production_batch(
                db,
                production_batch,
                completion_data.produced_volume_liters,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(production_batch)

        return production_batch

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
                ProductionBatchService._calculate_recipe_ingredient_consumption(
                    recipe_ingredient.required_quantity,
                    production_batch.planned_volume_liters,
                    recipe.target_volume_liters,
                )
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

            projections[raw_material.id]["planned_consumption"] += planned_consumption

        precision = Decimal("0.001")
        response = []

        for projection in projections.values():
            planned_consumption = projection["planned_consumption"].quantize(
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

    @staticmethod
    def _calculate_recipe_ingredient_consumption(
        required_quantity: Decimal,
        planned_volume_liters: Decimal,
        target_volume_liters: Decimal,
    ) -> Decimal:
        return (
            required_quantity * planned_volume_liters / target_volume_liters
        ).quantize(
            Decimal("0.001"),
            rounding=ROUND_HALF_UP,
        )
