from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal

from app.models.beer import Beer
from app.models.beer_presentation import BeerPresentation
from app.models.beer_presentation_packaging_material import (
    BeerPresentationPackagingMaterial,
)
from app.models.enums import PackagingFormatType
from app.models.packaging_format import PackagingFormat
from app.models.raw_material import RawMaterial
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.schemas.stock_coverage_requirement import (
    StockCoveragePlanResponse,
    StockCoverageRequirementResponse,
    StockCoverageWarningResponse,
)
from app.services.finished_product_stock_service import (
    FinishedProductStockService,
)
from sqlalchemy.orm import Session


QUANTITY_PRECISION = Decimal("0.001")


class StockCoverageService:
    @staticmethod
    def get_raw_material_plan(
        db: Session,
    ) -> StockCoveragePlanResponse:
        requirements_by_material: dict[
            int,
            dict[str, Decimal],
        ] = defaultdict(
            lambda: {
                "production": Decimal("0.000"),
                "packaging": Decimal("0.000"),
            }
        )

        warnings: list[StockCoverageWarningResponse] = []

        coverage_items = (
            FinishedProductStockService.get_keg_coverage(db)
        )

        beers = {
            beer.id: beer
            for beer in (
                db.query(Beer)
                .filter(Beer.active.is_(True))
                .all()
            )
        }

        current_recipes = {
            recipe.beer_id: recipe
            for recipe in (
                db.query(Recipe)
                .filter(
                    Recipe.active.is_(True),
                    Recipe.is_current.is_(True),
                )
                .all()
            )
        }

        ingredients_by_recipe: dict[
            int,
            list[RecipeIngredient],
        ] = defaultdict(list)

        for ingredient in (
            db.query(RecipeIngredient)
            .filter(RecipeIngredient.active.is_(True))
            .all()
        ):
            ingredients_by_recipe[ingredient.recipe_id].append(
                ingredient
            )

        for coverage in coverage_items:
            missing_volume = Decimal(
                coverage.shortage_volume_liters
            )

            if missing_volume <= 0:
                continue

            beer = beers.get(coverage.beer_id)
            recipe = current_recipes.get(coverage.beer_id)

            if not beer or not recipe:
                warnings.append(
                    StockCoverageWarningResponse(
                        source_type="beer",
                        source_code=(
                            beer.code
                            if beer is not None
                            else str(coverage.beer_id)
                        ),
                        source_name=coverage.beer_name,
                        detail=(
                            "La cerveza tiene faltante de cobertura "
                            "pero no posee una receta vigente."
                        ),
                    )
                )
                continue

            recipe_ingredients = ingredients_by_recipe.get(
                recipe.id,
                [],
            )

            if not recipe_ingredients:
                warnings.append(
                    StockCoverageWarningResponse(
                        source_type="beer",
                        source_code=beer.code,
                        source_name=beer.name,
                        detail=(
                            "La receta vigente no tiene "
                            "ingredientes configurados."
                        ),
                    )
                )
                continue

            scale_factor = (
                missing_volume
                / Decimal(recipe.target_volume_liters)
            )

            for ingredient in recipe_ingredients:
                required_quantity = (
                    Decimal(ingredient.required_quantity)
                    * scale_factor
                ).quantize(
                    QUANTITY_PRECISION,
                    rounding=ROUND_HALF_UP,
                )

                requirements_by_material[
                    ingredient.raw_material_id
                ]["production"] += required_quantity

        bottle_presentations = (
            db.query(BeerPresentation)
            .join(
                PackagingFormat,
                BeerPresentation.packaging_format_id
                == PackagingFormat.id,
            )
            .filter(
                BeerPresentation.active.is_(True),
                BeerPresentation.minimum_stock > 0,
                BeerPresentation.current_stock
                < BeerPresentation.minimum_stock,
                PackagingFormat.format_type.in_(
                    [
                        PackagingFormatType.BOTTLE,
                        PackagingFormatType.CAN,
                    ]
                ),
            )
            .all()
        )

        packaging_materials_by_presentation: dict[
            int,
            list[BeerPresentationPackagingMaterial],
        ] = defaultdict(list)

        for material in (
            db.query(BeerPresentationPackagingMaterial)
            .filter(
                BeerPresentationPackagingMaterial.active.is_(True)
            )
            .all()
        ):
            packaging_materials_by_presentation[
                material.beer_presentation_id
            ].append(material)

        for presentation in bottle_presentations:
            shortage_units = (
                presentation.minimum_stock
                - presentation.current_stock
            )

            packaging_materials = (
                packaging_materials_by_presentation.get(
                    presentation.id,
                    [],
                )
            )

            if not packaging_materials:
                warnings.append(
                    StockCoverageWarningResponse(
                        source_type="presentation",
                        source_code=presentation.code,
                        source_name=presentation.name,
                        detail=(
                            "La presentación está bajo su mínimo "
                            "pero no tiene materiales de envasado."
                        ),
                    )
                )
                continue

            for packaging_material in packaging_materials:
                required_quantity = (
                    Decimal(
                        packaging_material.required_quantity
                    )
                    * Decimal(shortage_units)
                ).quantize(
                    QUANTITY_PRECISION,
                    rounding=ROUND_HALF_UP,
                )

                requirements_by_material[
                    packaging_material.raw_material_id
                ]["packaging"] += required_quantity

        raw_material_ids = list(
            requirements_by_material.keys()
        )

        if not raw_material_ids:
            return StockCoveragePlanResponse(
                requirements=[],
                warnings=warnings,
            )

        raw_materials = (
            db.query(RawMaterial)
            .filter(RawMaterial.id.in_(raw_material_ids))
            .all()
        )

        requirements = []

        for raw_material in raw_materials:
            quantities = requirements_by_material[
                raw_material.id
            ]

            production_required = quantities[
                "production"
            ].quantize(
                QUANTITY_PRECISION,
                rounding=ROUND_HALF_UP,
            )

            packaging_required = quantities[
                "packaging"
            ].quantize(
                QUANTITY_PRECISION,
                rounding=ROUND_HALF_UP,
            )

            total_required = (
                production_required
                + packaging_required
            ).quantize(
                QUANTITY_PRECISION,
                rounding=ROUND_HALF_UP,
            )

            current_stock = Decimal(
                raw_material.current_stock
            )
            minimum_stock = Decimal(
                raw_material.minimum_stock
            )

            projected_stock = (
                current_stock - total_required
            ).quantize(
                QUANTITY_PRECISION,
                rounding=ROUND_HALF_UP,
            )

            shortage = max(
                Decimal("0.000"),
                (
                    minimum_stock
                    + total_required
                    - current_stock
                ),
            ).quantize(
                QUANTITY_PRECISION,
                rounding=ROUND_HALF_UP,
            )

            requirements.append(
                StockCoverageRequirementResponse(
                    raw_material_id=raw_material.id,
                    raw_material_code=raw_material.code,
                    raw_material_name=raw_material.name,
                    unit_symbol=raw_material.unit.symbol,
                    production_required_quantity=(
                        production_required
                    ),
                    packaging_required_quantity=(
                        packaging_required
                    ),
                    total_required_quantity=total_required,
                    current_stock=current_stock,
                    minimum_stock=minimum_stock,
                    projected_stock=projected_stock,
                    shortage_quantity=shortage,
                    has_shortage=shortage > 0,
                )
            )

        requirements.sort(
            key=lambda item: item.raw_material_name.lower()
        )

        return StockCoveragePlanResponse(
            requirements=requirements,
            warnings=warnings,
        )