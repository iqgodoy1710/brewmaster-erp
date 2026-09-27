from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from app.common.exceptions import (
    BeerPresentationHasNoPackagingMaterialsError,
    BeerPresentationNotFoundError,
    InactiveBeerPresentationError,
    InactiveKegError,
    InactiveRawMaterialError,
    InsufficientBeerPresentationStockError,
    InsufficientStockError,
    InvalidKegRepackagingError,
    InvalidKegRepackagingReversalError,
    KegNotFoundError,
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
    create_repackaging_consumption_movement,
    create_repackaging_receipt_movement,
    create_repackaging_reversal_in_movement,
    create_repackaging_reversal_out_movement,
    get_repackaging_stock_movements,
)
from app.crud.keg import get_keg_by_id, update_keg_state
from app.crud.keg_movement import (
    create_keg_movement,
    get_latest_keg_movement,
    get_repackaging_keg_movement,
)
from app.crud.keg_repackaging_run import (
    create_keg_repackaging_run,
    get_keg_repackaging_run_by_code,
    get_keg_repackaging_runs,
    get_keg_repackaging_runs_by_keg,
    reverse_keg_repackaging_run,
)
from app.crud.raw_material import (
    get_raw_material_by_id,
    update_raw_material_stock,
)
from app.crud.raw_material_stock_movement import (
    create_repackaging_material_consumption_movement,
    create_repackaging_material_reversal_movement,
    get_repackaging_material_movements,
)
from app.models.enums import (
    BeerPresentationStockMovementType,
    KegMovementType,
    KegStatus,
    PackagingFormatType,
)
from app.schemas.keg_repackaging_run import (
    KegRepackagingRunCreate,
    KegRepackagingRunReverse,
)
from app.services.code_service import generate_code
from sqlalchemy.orm import Session


class KegRepackagingRunService:
    @staticmethod
    def get_all(db: Session):
        return get_keg_repackaging_runs(db)

    @staticmethod
    def create(
        db: Session,
        repackaging_data: KegRepackagingRunCreate,
        performed_by_user_id: int | None = None,
    ):
        keg = get_keg_by_id(db, repackaging_data.keg_id)

        if not keg:
            raise KegNotFoundError("The keg does not exist.")

        if not keg.active:
            raise InactiveKegError("Cannot repackage beer from an inactive keg.")

        if keg.status not in {
            KegStatus.FILLED,
            KegStatus.TAPPED,
        }:
            raise InvalidKegRepackagingError(
                "Only filled or tapped kegs can be repackaged."
            )

        if keg.beer_presentation_id is None or keg.production_batch_id is None:
            raise InvalidKegRepackagingError(
                "The keg does not have beer and batch traceability."
            )

        source_presentation = get_beer_presentation_by_id(
            db,
            keg.beer_presentation_id,
        )
        if not source_presentation:
            raise BeerPresentationNotFoundError(
                "The keg source beer presentation does not exist."
            )

        target_presentation = get_beer_presentation_by_id(
            db,
            repackaging_data.target_beer_presentation_id,
        )
        if not target_presentation:
            raise BeerPresentationNotFoundError(
                "The target beer presentation does not exist."
            )

        if not target_presentation.active:
            raise InactiveBeerPresentationError(
                "Cannot repackage into an inactive beer presentation."
            )

        if source_presentation.packaging_format.format_type != PackagingFormatType.KEG:
            raise InvalidKegRepackagingError(
                "The source presentation must use a keg format."
            )

        if (
            target_presentation.packaging_format.format_type
            != PackagingFormatType.BOTTLE
        ):
            raise InvalidKegRepackagingError(
                "The target presentation must use a bottle format."
            )

        if source_presentation.beer_id != target_presentation.beer_id:
            raise InvalidKegRepackagingError(
                "The target presentation must belong to the same beer."
            )

        packaged_volume_liters = (
            target_presentation.packaging_format.capacity_liters
            * Decimal(repackaging_data.packaged_quantity)
        ).quantize(
            Decimal("0.001"),
            rounding=ROUND_HALF_UP,
        )

        remaining_volume_liters = (repackaging_data.remaining_volume_liters).quantize(
            Decimal("0.001"),
            rounding=ROUND_HALF_UP,
        )

        if remaining_volume_liters > keg.current_volume_liters:
            raise InvalidKegRepackagingError(
                "The remaining volume exceeds the keg current volume."
            )

        waste_volume_liters = (
            keg.current_volume_liters - packaged_volume_liters - remaining_volume_liters
        ).quantize(
            Decimal("0.001"),
            rounding=ROUND_HALF_UP,
        )

        if waste_volume_liters < 0:
            raise InvalidKegRepackagingError(
                "The produced bottles and remaining volume exceed "
                "the keg current volume."
            )

        packaging_materials = get_beer_presentation_packaging_materials(
            db,
            target_presentation.id,
        )
        if not packaging_materials:
            raise BeerPresentationHasNoPackagingMaterialsError(
                "The target beer presentation has no packaging materials."
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

            required_quantity = (
                packaging_material.required_quantity
                * Decimal(repackaging_data.packaged_quantity)
            ).quantize(
                Decimal("0.001"),
                rounding=ROUND_HALF_UP,
            )

            if raw_material.current_stock < required_quantity:
                raise InsufficientStockError(
                    "There is not enough stock for a packaging material."
                )

            material_consumptions.append((raw_material, required_quantity))

        existing_repackaging_runs = get_keg_repackaging_runs_by_keg(db, keg.id)
        consumes_source_presentation = (
            keg.status == KegStatus.FILLED and not existing_repackaging_runs
        )

        if consumes_source_presentation and source_presentation.current_stock < 1:
            raise InsufficientBeerPresentationStockError(
                "There is not enough stock for the source keg presentation."
            )

        new_keg_status = (
            KegStatus.DIRTY
            if remaining_volume_liters == Decimal("0.000")
            else KegStatus.TAPPED
        )

        generated_code = generate_code(
            db,
            "keg_repackaging_run",
        )

        try:
            repackaging_run = create_keg_repackaging_run(
                db,
                code=generated_code,
                keg_id=keg.id,
                source_beer_presentation_id=source_presentation.id,
                target_beer_presentation_id=target_presentation.id,
                production_batch_id=keg.production_batch_id,
                packaged_quantity=repackaging_data.packaged_quantity,
                packaged_volume_liters=packaged_volume_liters,
                remaining_volume_liters=remaining_volume_liters,
                waste_volume_liters=waste_volume_liters,
                performed_by_user_id=performed_by_user_id,
                notes=repackaging_data.notes,
                occurred_at=repackaging_data.occurred_at,
            )

            if consumes_source_presentation:
                create_repackaging_consumption_movement(
                    db,
                    beer_presentation_id=source_presentation.id,
                    keg_repackaging_run_id=repackaging_run.id,
                    quantity=1,
                    reference=repackaging_run.code,
                    notes=(
                        "Source keg presentation consumed by "
                        f"repackaging run {repackaging_run.code}."
                    ),
                    occurred_at=repackaging_data.occurred_at,
                )
                update_beer_presentation_stock(
                    db,
                    source_presentation,
                    source_presentation.current_stock - 1,
                )

            create_repackaging_receipt_movement(
                db,
                beer_presentation_id=target_presentation.id,
                keg_repackaging_run_id=repackaging_run.id,
                quantity=repackaging_data.packaged_quantity,
                reference=repackaging_run.code,
                notes=(
                    f"Bottle receipt from keg repackaging run {repackaging_run.code}."
                ),
                occurred_at=repackaging_data.occurred_at,
            )
            update_beer_presentation_stock(
                db,
                target_presentation,
                (
                    target_presentation.current_stock
                    + repackaging_data.packaged_quantity
                ),
            )

            for raw_material, required_quantity in material_consumptions:
                create_repackaging_material_consumption_movement(
                    db,
                    raw_material_id=raw_material.id,
                    keg_repackaging_run_id=repackaging_run.id,
                    quantity=required_quantity,
                    reference=repackaging_run.code,
                    notes=(
                        "Packaging material consumption for keg "
                        f"repackaging run {repackaging_run.code}."
                    ),
                    occurred_at=repackaging_data.occurred_at,
                )
                update_raw_material_stock(
                    db,
                    raw_material,
                    raw_material.current_stock - required_quantity,
                )

            create_keg_movement(
                db,
                keg_id=keg.id,
                movement_type=KegMovementType.REPACKAGING,
                previous_status=keg.status,
                new_status=new_keg_status,
                resulting_volume_liters=remaining_volume_liters,
                beer_presentation_id=source_presentation.id,
                production_batch_id=keg.production_batch_id,
                keg_repackaging_run_id=repackaging_run.id,
                reference=repackaging_run.code,
                notes=(
                    repackaging_data.notes
                    or (f"Keg repackaged into bottles by run {repackaging_run.code}.")
                ),
                occurred_at=repackaging_data.occurred_at,
                performed_by_user_id=performed_by_user_id,
            )

            update_keg_state(
                db,
                keg,
                status=new_keg_status,
                current_volume_liters=remaining_volume_liters,
                beer_presentation_id=(
                    None
                    if new_keg_status == KegStatus.DIRTY
                    else source_presentation.id
                ),
                production_batch_id=(
                    None
                    if new_keg_status == KegStatus.DIRTY
                    else keg.production_batch_id
                ),
                customer_id=None,
            )

            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(repackaging_run)

        return repackaging_run

    @staticmethod
    def reverse(
        db: Session,
        code: str,
        reversal_data: KegRepackagingRunReverse,
        performed_by_user_id: int | None = None,
    ):
        repackaging_run = get_keg_repackaging_run_by_code(
            db,
            code,
        )

        if not repackaging_run:
            raise InvalidKegRepackagingReversalError(
                "The keg repackaging run does not exist."
            )

        if repackaging_run.reversed_at is not None:
            raise InvalidKegRepackagingReversalError(
                "The keg repackaging run has already been reversed."
            )

        keg = get_keg_by_id(
            db,
            repackaging_run.keg_id,
        )
        if not keg:
            raise KegNotFoundError("The keg does not exist.")

        original_keg_movement = get_repackaging_keg_movement(
            db,
            repackaging_run.id,
        )
        if not original_keg_movement:
            raise InvalidKegRepackagingReversalError(
                "The original keg movement does not exist."
            )

        latest_keg_movement = get_latest_keg_movement(
            db,
            keg.id,
        )
        if (
            not latest_keg_movement
            or latest_keg_movement.id != original_keg_movement.id
        ):
            raise InvalidKegRepackagingReversalError(
                "The keg has subsequent movements and "
                "the repackaging cannot be reversed."
            )

        source_presentation = get_beer_presentation_by_id(
            db,
            repackaging_run.source_beer_presentation_id,
        )
        target_presentation = get_beer_presentation_by_id(
            db,
            repackaging_run.target_beer_presentation_id,
        )

        if not source_presentation or not target_presentation:
            raise BeerPresentationNotFoundError("A beer presentation does not exist.")

        if target_presentation.current_stock < repackaging_run.packaged_quantity:
            raise InvalidKegRepackagingReversalError(
                "There is not enough bottle stock to reverse this repackaging."
            )

        presentation_movements = get_repackaging_stock_movements(
            db,
            repackaging_run.id,
        )

        source_consumption_movement = next(
            (
                movement
                for movement in presentation_movements
                if movement.movement_type
                == BeerPresentationStockMovementType.REPACKAGING_CONSUMPTION
            ),
            None,
        )

        target_receipt_movement = next(
            (
                movement
                for movement in presentation_movements
                if movement.movement_type
                == BeerPresentationStockMovementType.REPACKAGING_RECEIPT
            ),
            None,
        )

        if not target_receipt_movement:
            raise InvalidKegRepackagingReversalError(
                "The original bottle stock movement does not exist."
            )

        material_movements = get_repackaging_material_movements(
            db,
            repackaging_run.id,
        )

        materials_to_restore = []

        for material_movement in material_movements:
            raw_material = get_raw_material_by_id(
                db,
                material_movement.raw_material_id,
            )

            if not raw_material:
                raise RawMaterialNotFoundError("A packaging material does not exist.")

            materials_to_restore.append(
                (
                    raw_material,
                    material_movement.quantity,
                )
            )

        reversed_at = datetime.now()
        reversal_reference = f"REV-{repackaging_run.code}"

        original_volume_liters = (
            repackaging_run.packaged_volume_liters
            + repackaging_run.remaining_volume_liters
            + repackaging_run.waste_volume_liters
        )

        try:
            create_repackaging_reversal_out_movement(
                db,
                beer_presentation_id=target_presentation.id,
                keg_repackaging_run_id=repackaging_run.id,
                quantity=repackaging_run.packaged_quantity,
                reference=reversal_reference,
                notes=(
                    f"Bottle stock reversal for repackaging run {repackaging_run.code}."
                ),
                occurred_at=reversed_at,
            )

            update_beer_presentation_stock(
                db,
                target_presentation,
                (target_presentation.current_stock - repackaging_run.packaged_quantity),
            )

            if source_consumption_movement:
                create_repackaging_reversal_in_movement(
                    db,
                    beer_presentation_id=source_presentation.id,
                    keg_repackaging_run_id=repackaging_run.id,
                    quantity=source_consumption_movement.quantity,
                    reference=reversal_reference,
                    notes=(
                        "Source keg stock reversal for "
                        f"repackaging run {repackaging_run.code}."
                    ),
                    occurred_at=reversed_at,
                )

                update_beer_presentation_stock(
                    db,
                    source_presentation,
                    (
                        source_presentation.current_stock
                        + source_consumption_movement.quantity
                    ),
                )

            for raw_material, quantity in materials_to_restore:
                create_repackaging_material_reversal_movement(
                    db,
                    raw_material_id=raw_material.id,
                    keg_repackaging_run_id=repackaging_run.id,
                    quantity=quantity,
                    reference=reversal_reference,
                    notes=(
                        "Packaging material reversal for "
                        f"repackaging run {repackaging_run.code}."
                    ),
                    occurred_at=reversed_at,
                )

                update_raw_material_stock(
                    db,
                    raw_material,
                    raw_material.current_stock + quantity,
                )

            create_keg_movement(
                db,
                keg_id=keg.id,
                movement_type=(KegMovementType.REPACKAGING_REVERSAL),
                previous_status=keg.status,
                new_status=original_keg_movement.previous_status,
                resulting_volume_liters=original_volume_liters,
                beer_presentation_id=source_presentation.id,
                production_batch_id=(repackaging_run.production_batch_id),
                keg_repackaging_run_id=repackaging_run.id,
                reference=reversal_reference,
                notes=reversal_data.reason,
                occurred_at=reversed_at,
                performed_by_user_id=performed_by_user_id,
            )

            update_keg_state(
                db,
                keg,
                status=original_keg_movement.previous_status,
                current_volume_liters=original_volume_liters,
                beer_presentation_id=source_presentation.id,
                production_batch_id=(repackaging_run.production_batch_id),
                customer_id=None,
            )

            reverse_keg_repackaging_run(
                db,
                repackaging_run,
                reversed_at=reversed_at,
                reversed_by_user_id=performed_by_user_id,
                reversal_reason=reversal_data.reason,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        db.refresh(repackaging_run)

        return repackaging_run
