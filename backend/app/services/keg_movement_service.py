from decimal import Decimal

from app.common.exceptions import (
    InactiveKegError,
    InvalidKegFillingError,
    InvalidKegRemnantTransferError,
    InvalidKegReturnError,
    InvalidKegWashingError,
    KegNotFoundError,
    PackagingRunNotFoundError,
)
from app.crud.beer_presentation import get_beer_presentation_by_id
from app.crud.keg import (
    get_keg_by_id,
    update_keg_state,
)
from app.crud.keg_movement import (
    count_filling_movements_for_packaging_run,
    create_keg_movement,
    get_keg_movements,
)
from app.crud.packaging_run import get_packaging_run_by_id
from app.crud.production_batch import (
    get_production_batch_by_id,
)
from app.models.enums import KegMovementType, KegStatus, ProductionBatchStatus
from app.schemas.keg_movement import (
    KegFillCreate,
    KegFillFromBulkCreate,
    KegRemnantTransferCreate,
    KegRemnantTransferResponse,
    KegReturnCreate,
    KegWashCreate,
)
from app.schemas.packaging_run import PackagingRunCreate
from app.services.packaging_run_service import PackagingRunService
from sqlalchemy.orm import Session


class KegMovementService:
    @staticmethod
    def get_all_by_keg(
        db: Session,
        keg_id: int,
    ):
        keg = get_keg_by_id(db, keg_id)

        if not keg:
            raise KegNotFoundError("The keg does not exist.")

        return get_keg_movements(db, keg_id)

    @staticmethod
    def fill(
        db: Session,
        filling_data: KegFillCreate,
        performed_by_user_id: int | None = None,
    ):
        keg = get_keg_by_id(db, filling_data.keg_id)

        if not keg:
            raise KegNotFoundError("The keg does not exist.")

        if not keg.active:
            raise InactiveKegError("Cannot fill an inactive keg.")

        if keg.status != KegStatus.CLEAN_AVAILABLE:
            raise InvalidKegFillingError("Only clean available kegs can be filled.")

        packaging_run = get_packaging_run_by_id(
            db,
            filling_data.packaging_run_id,
        )
        if not packaging_run:
            raise PackagingRunNotFoundError("The packaging run does not exist.")

        if not packaging_run.active:
            raise InvalidKegFillingError(
                "Cannot fill a keg from an inactive packaging run."
            )

        beer_presentation = get_beer_presentation_by_id(
            db,
            packaging_run.beer_presentation_id,
        )
        if not beer_presentation:
            raise InvalidKegFillingError(
                "The packaging run beer presentation does not exist."
            )

        if keg.packaging_format_id != beer_presentation.packaging_format_id:
            raise InvalidKegFillingError(
                "The keg format does not match the packaging run presentation."
            )

        filled_kegs_count = count_filling_movements_for_packaging_run(
            db,
            packaging_run.id,
        )
        if filled_kegs_count >= packaging_run.packaged_quantity:
            raise InvalidKegFillingError(
                "All units from this packaging run are already assigned to kegs."
            )

        resulting_volume_liters = keg.packaging_format.capacity_liters

        try:
            movement = create_keg_movement(
                db,
                keg_id=keg.id,
                movement_type=KegMovementType.FILLING,
                previous_status=keg.status,
                new_status=KegStatus.FILLED,
                resulting_volume_liters=resulting_volume_liters,
                beer_presentation_id=beer_presentation.id,
                production_batch_id=packaging_run.production_batch_id,
                packaging_run_id=packaging_run.id,
                reference=packaging_run.code,
                notes=(
                    filling_data.notes
                    or f"Keg filling from packaging run {packaging_run.code}."
                ),
                occurred_at=filling_data.occurred_at,
                performed_by_user_id=performed_by_user_id,
            )

            update_keg_state(
                db,
                keg,
                status=KegStatus.FILLED,
                current_volume_liters=resulting_volume_liters,
                beer_presentation_id=beer_presentation.id,
                production_batch_id=packaging_run.production_batch_id,
                customer_id=None,
            )

            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(movement)

        return movement

    @staticmethod
    def fill_from_bulk(
        db: Session,
        filling_data: KegFillFromBulkCreate,
        performed_by_user_id: int | None = None,
    ):
        packaging_run = PackagingRunService.create(
            db,
            PackagingRunCreate(
                production_batch_id=filling_data.production_batch_id,
                beer_presentation_id=filling_data.beer_presentation_id,
                packaged_quantity=1,
                notes=(
                    filling_data.notes
                    or "Automatically generated for direct keg filling."
                ),
            ),
            commit=False,
        )

        return KegMovementService.fill(
            db,
            KegFillCreate(
                keg_id=filling_data.keg_id,
                packaging_run_id=packaging_run.id,
                notes=filling_data.notes,
                occurred_at=filling_data.occurred_at,
            ),
            performed_by_user_id=performed_by_user_id,
        )

    @staticmethod
    def return_keg(
        db: Session,
        return_data: KegReturnCreate,
        performed_by_user_id: int | None = None,
    ):
        keg = get_keg_by_id(db, return_data.keg_id)

        if not keg:
            raise KegNotFoundError("The keg does not exist.")

        if not keg.active:
            raise InactiveKegError("Cannot return an inactive keg.")

        if keg.status != KegStatus.AT_CUSTOMER:
            raise InvalidKegReturnError("Only kegs at a customer can be returned.")

        if return_data.resulting_volume_liters > keg.packaging_format.capacity_liters:
            raise InvalidKegReturnError("The returned volume exceeds the keg capacity.")

        returned_empty = return_data.resulting_volume_liters == 0
        new_status = KegStatus.DIRTY if returned_empty else KegStatus.TAPPED

        previous_customer_id = keg.customer_id
        previous_beer_presentation_id = keg.beer_presentation_id
        previous_production_batch_id = keg.production_batch_id

        try:
            movement = create_keg_movement(
                db,
                keg_id=keg.id,
                movement_type=KegMovementType.RETURN,
                previous_status=keg.status,
                new_status=new_status,
                resulting_volume_liters=(return_data.resulting_volume_liters),
                beer_presentation_id=previous_beer_presentation_id,
                production_batch_id=previous_production_batch_id,
                customer_id=previous_customer_id,
                reference=keg.code,
                notes=(return_data.notes or f"Keg return for {keg.code}."),
                occurred_at=return_data.occurred_at,
                performed_by_user_id=performed_by_user_id,
            )

            update_keg_state(
                db,
                keg,
                status=new_status,
                current_volume_liters=(return_data.resulting_volume_liters),
                beer_presentation_id=(
                    None if returned_empty else previous_beer_presentation_id
                ),
                production_batch_id=(
                    None if returned_empty else previous_production_batch_id
                ),
                customer_id=None,
            )

            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(movement)

        return movement


    @staticmethod
    def wash(
        db: Session,
        washing_data: KegWashCreate,
        performed_by_user_id: int | None = None,
    ):
        keg = get_keg_by_id(db, washing_data.keg_id)

        if not keg:
            raise KegNotFoundError("The keg does not exist.")

        if not keg.active:
            raise InactiveKegError("Cannot wash an inactive keg.")

        if keg.status != KegStatus.DIRTY:
            raise InvalidKegWashingError("Only dirty kegs can be washed.")

        if keg.current_volume_liters != 0:
            raise InvalidKegWashingError("A keg with remaining beer cannot be washed.")

        try:
            movement = create_keg_movement(
                db,
                keg_id=keg.id,
                movement_type=KegMovementType.WASHING,
                previous_status=keg.status,
                new_status=KegStatus.CLEAN_AVAILABLE,
                resulting_volume_liters=0,
                reference=keg.code,
                notes=(washing_data.notes or f"Keg washing for {keg.code}."),
                occurred_at=washing_data.occurred_at,
                performed_by_user_id=performed_by_user_id,
            )

            update_keg_state(
                db,
                keg,
                status=KegStatus.CLEAN_AVAILABLE,
                current_volume_liters=0,
                beer_presentation_id=None,
                production_batch_id=None,
                customer_id=None,
            )

            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(movement)

        return movement

    @staticmethod
    def transfer_remnants(
        db: Session,
        transfer_data: KegRemnantTransferCreate,
        performed_by_user_id: int | None = None,
    ) -> KegRemnantTransferResponse:
        if (
            len(transfer_data.source_keg_ids)
            != len(set(transfer_data.source_keg_ids))
        ):
            raise InvalidKegRemnantTransferError(
                "A keg can only be selected once for a remnant transfer."
            )

        source_kegs = []
        source_beer_presentation_id: int | None = None
        source_production_batch_id: int | None = None
        recovered_volume_liters = Decimal("0.000")

        for keg_id in transfer_data.source_keg_ids:
            keg = get_keg_by_id(db, keg_id)

            if not keg:
                raise KegNotFoundError("The keg does not exist.")

            if not keg.active:
                raise InactiveKegError(
                    "Cannot transfer remnants from an inactive keg."
                )

            if keg.status != KegStatus.TAPPED:
                raise InvalidKegRemnantTransferError(
                    "Only tapped kegs can provide remnants."
                )

            if keg.current_volume_liters <= 0:
                raise InvalidKegRemnantTransferError(
                    "A source keg must contain remaining beer."
                )

            if (
                keg.beer_presentation_id is None
                or keg.production_batch_id is None
            ):
                raise InvalidKegRemnantTransferError(
                    "A source keg must have beer and production batch traceability."
                )

            if source_beer_presentation_id is None:
                source_beer_presentation_id = (
                    keg.beer_presentation_id
                )
                source_production_batch_id = (
                    keg.production_batch_id
                )
            elif (
                keg.beer_presentation_id
                != source_beer_presentation_id
                or keg.production_batch_id
                != source_production_batch_id
            ):
                raise InvalidKegRemnantTransferError(
                    "All source kegs must belong to the same beer presentation and production batch."
                )

            recovered_volume_liters += keg.current_volume_liters
            source_kegs.append(keg)

        production_batch = get_production_batch_by_id(
            db,
            source_production_batch_id,
        )
        if not production_batch:
            raise InvalidKegRemnantTransferError(
                "The source production batch does not exist."
            )

        if (
            not production_batch.active
            or production_batch.status
            != ProductionBatchStatus.COMPLETED
        ):
            raise InvalidKegRemnantTransferError(
                "Remnants can only be returned to an active completed production batch."
            )

        resulting_available_bulk_volume_liters = (
            production_batch.available_bulk_volume_liters
            + recovered_volume_liters
        )

        if (
            production_batch.produced_volume_liters is not None
            and resulting_available_bulk_volume_liters
            > production_batch.produced_volume_liters
        ):
            raise InvalidKegRemnantTransferError(
                "The recovered volume exceeds the original produced batch volume."
            )

        source_movements = []

        try:
            for keg in source_kegs:
                movement = create_keg_movement(
                    db,
                    keg_id=keg.id,
                    movement_type=KegMovementType.REMNANT_TRANSFER,
                    previous_status=keg.status,
                    new_status=KegStatus.DIRTY,
                    resulting_volume_liters=Decimal("0.000"),
                    beer_presentation_id=keg.beer_presentation_id,
                    production_batch_id=keg.production_batch_id,
                    reference=production_batch.code,
                    notes=(
                        transfer_data.notes
                        or (
                            "Keg remnant transferred to production batch "
                            f"{production_batch.code}."
                        )
                    ),
                    occurred_at=transfer_data.occurred_at,
                    performed_by_user_id=performed_by_user_id,
                )
                source_movements.append(movement)

                update_keg_state(
                    db,
                    keg,
                    status=KegStatus.DIRTY,
                    current_volume_liters=Decimal("0.000"),
                    beer_presentation_id=None,
                    production_batch_id=None,
                    customer_id=None,
                )

            production_batch.available_bulk_volume_liters = (
                resulting_available_bulk_volume_liters
            )
            db.flush()

            db.commit()
        except Exception:
            db.rollback()
            raise

        for movement in source_movements:
            db.refresh(movement)

        return KegRemnantTransferResponse(
            production_batch_id=production_batch.id,
            recovered_volume_liters=recovered_volume_liters,
            resulting_available_bulk_volume_liters=(
                resulting_available_bulk_volume_liters
            ),
            source_movements=source_movements,
        )