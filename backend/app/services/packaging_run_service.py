from decimal import ROUND_HALF_UP, Decimal

from app.common.exceptions import (
    BeerPresentationHasNoPackagingMaterialsError,
    BeerPresentationNotFoundError,
    InactiveBeerPresentationError,
    InactiveRawMaterialError,
    InsufficientBulkBeerError,
    InsufficientStockError,
    InvalidPackagingRunError,
    InvalidProductionBatchStatusError,
    ProductionBatchNotFoundError,
    RawMaterialNotFoundError,
)
from app.crud.beer_presentation import (
    get_beer_presentation_by_id,
    update_beer_presentation_stock,
)
from app.crud.beer_presentation_packaging_material import (
    get_beer_presentation_packaging_materials,
)
from app.crud.beer_presentation_stock_movement import (
    create_packaging_receipt_movement,
)
from app.crud.packaging_run import (
    create_packaging_run,
    get_packaging_runs,
)
from app.crud.production_batch import (
    get_packaged_volume_for_production_batch,
    get_production_batch_by_id,
    update_available_bulk_volume,
)
from app.crud.raw_material import (
    get_raw_material_by_id,
    update_raw_material_stock,
)
from app.crud.raw_material_stock_movement import (
    create_packaging_material_consumption_movement,
)
from app.models.enums import (
    PackagingFormatType,
    ProductionBatchStatus,
)
from app.schemas.packaging_run import PackagingRunCreate
from app.services.code_service import generate_code
from sqlalchemy.orm import Session


class PackagingRunService:
    @staticmethod
    def get_all(db: Session):
        return get_packaging_runs(db)

    @staticmethod
    def create(
        db: Session,
        packaging_run_data: PackagingRunCreate,
        commit: bool = True,
    ):

        production_batch = get_production_batch_by_id(
            db,
            packaging_run_data.production_batch_id,
        )
        if not production_batch.active or production_batch.status not in {
            ProductionBatchStatus.COMPLETED,
            ProductionBatchStatus.IN_PROGRESS,
        }:
            raise InvalidProductionBatchStatusError(
                "Only completed or in-progress production batches can be packaged."
            )

        beer_presentation = get_beer_presentation_by_id(
            db,
            packaging_run_data.beer_presentation_id,
        )
        if not beer_presentation:
            raise BeerPresentationNotFoundError("The beer presentation does not exist.")

        if not beer_presentation.active:
            raise InactiveBeerPresentationError(
                "Cannot package an inactive beer presentation."
            )

        if production_batch.recipe.beer_id != beer_presentation.beer_id:
            raise InvalidPackagingRunError(
                "The beer presentation does not match the production batch beer."
            )
        if beer_presentation.packaging_format.format_type != PackagingFormatType.KEG:
            raise InvalidPackagingRunError(
                "Primary packaging runs can only use keg presentations."
            )

        packaging_materials = get_beer_presentation_packaging_materials(
            db,
            beer_presentation.id,
        )
        if not packaging_materials:
            raise BeerPresentationHasNoPackagingMaterialsError(
                "The beer presentation has no packaging materials."
            )

        packaged_volume_liters = PackagingRunService._calculate_packaged_volume(
            beer_presentation.packaging_format.capacity_liters,
            packaging_run_data.packaged_quantity,
        )

        new_available_bulk_volume: Decimal | None = None

        if production_batch.status == ProductionBatchStatus.COMPLETED:
            if production_batch.available_bulk_volume_liters < packaged_volume_liters:
                raise InsufficientBulkBeerError(
                    "There is not enough bulk beer available for this packaging run."
                )

            new_available_bulk_volume = (
                production_batch.available_bulk_volume_liters - packaged_volume_liters
            )
        else:
            already_packaged_volume = get_packaged_volume_for_production_batch(
                db,
                production_batch.id,
            )
            provisional_packaging_limit = (
                production_batch.planned_volume_liters * Decimal("1.10")
            ).quantize(
                Decimal("0.001"),
                rounding=ROUND_HALF_UP,
            )

            if (
                already_packaged_volume + packaged_volume_liters
                > provisional_packaging_limit
            ):
                raise InsufficientBulkBeerError(
                    "The provisional packaging limit for this production batch was exceeded."
                )

        material_consumptions = []

        for packaging_material in packaging_materials:
            raw_material = get_raw_material_by_id(
                db,
                packaging_material.raw_material_id,
            )
            if not raw_material:
                raise RawMaterialNotFoundError("A packaging material does not exist.")

            if not raw_material.active:
                raise InactiveRawMaterialError(
                    "Cannot consume an inactive packaging material."
                )

            required_quantity = PackagingRunService._calculate_material_consumption(
                packaging_material.required_quantity,
                packaging_run_data.packaged_quantity,
            )

            if raw_material.current_stock < required_quantity:
                raise InsufficientStockError(
                    "There is not enough stock for a packaging material."
                )

            material_consumptions.append((raw_material, required_quantity))

        new_presentation_stock = (
            beer_presentation.current_stock + packaging_run_data.packaged_quantity
        )
        generated_code = generate_code(
            db,
            "packaging_run",
        )

        try:
            packaging_run = create_packaging_run(
                db,
                packaging_run_data,
                generated_code,
                packaged_volume_liters,
            )
            create_packaging_receipt_movement(
                db,
                beer_presentation_id=beer_presentation.id,
                packaging_run_id=packaging_run.id,
                quantity=packaging_run_data.packaged_quantity,
                reference=packaging_run.code,
                notes=(
                    f"Finished product receipt for packaging run {packaging_run.code}."
                ),
            )

            if new_available_bulk_volume is not None:
                update_available_bulk_volume(
                    db,
                    production_batch,
                    new_available_bulk_volume,
                )
            update_beer_presentation_stock(
                db,
                beer_presentation,
                new_presentation_stock,
            )

            for raw_material, required_quantity in material_consumptions:
                create_packaging_material_consumption_movement(
                    db,
                    raw_material_id=raw_material.id,
                    packaging_run_id=packaging_run.id,
                    quantity=required_quantity,
                    reference=packaging_run.code,
                    notes=(
                        "Packaging material consumption for packaging run "
                        f"{packaging_run.code}."
                    ),
                )
                update_raw_material_stock(
                    db,
                    raw_material,
                    raw_material.current_stock - required_quantity,
                )

            if commit:
                db.commit()
            else:
                db.flush()
        except Exception:
            db.rollback()
            raise

        if commit:
            db.refresh(packaging_run)

        return packaging_run

    @staticmethod
    def _calculate_packaged_volume(
        capacity_liters: Decimal,
        packaged_quantity: int,
    ) -> Decimal:
        return (capacity_liters * Decimal(packaged_quantity)).quantize(
            Decimal("0.001"),
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _calculate_material_consumption(
        required_quantity: Decimal,
        packaged_quantity: int,
    ) -> Decimal:
        return (required_quantity * Decimal(packaged_quantity)).quantize(
            Decimal("0.001"),
            rounding=ROUND_HALF_UP,
        )
