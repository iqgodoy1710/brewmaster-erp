from app.common.exceptions import (
    BeerPresentationNotFoundError,
    InactiveBeerPresentationError,
    InsufficientBeerPresentationStockError,
    InvalidBottlePasteurizationError,
)
from app.crud.beer_presentation import (
    get_beer_presentation_by_id,
    update_beer_presentation_stock,
)
from app.crud.beer_presentation_stock_movement import (
    create_pasteurization_waste_movement,
)
from app.crud.bottle_pasteurization_run import (
    create_bottle_pasteurization_run,
    get_bottle_pasteurization_runs,
)
from app.models.enums import PackagingFormatType
from app.models.user import User
from app.schemas.bottle_pasteurization_run import (
    BottlePasteurizationRunCreate,
)
from app.services.code_service import generate_code
from sqlalchemy.orm import Session


class BottlePasteurizationRunService:
    @staticmethod
    def get_all(db: Session):
        return get_bottle_pasteurization_runs(db)

    @staticmethod
    def create(
        db: Session,
        pasteurization_data: BottlePasteurizationRunCreate,
        current_user: User | None,
    ):
        beer_presentation = get_beer_presentation_by_id(
            db,
            pasteurization_data.beer_presentation_id,
        )

        if not beer_presentation:
            raise BeerPresentationNotFoundError(
                "The beer presentation does not exist."
            )

        if not beer_presentation.active:
            raise InactiveBeerPresentationError(
                "Cannot pasteurize an inactive beer presentation."
            )

        if (
            beer_presentation.packaging_format.format_type
            != PackagingFormatType.BOTTLE
        ):
            raise InvalidBottlePasteurizationError(
                "Only bottle presentations can be pasteurized."
            )

        if (
            pasteurization_data.approved_quantity
            > pasteurization_data.processed_quantity
        ):
            raise InvalidBottlePasteurizationError(
                "The approved quantity cannot exceed "
                "the processed quantity."
            )

        if (
            pasteurization_data.processed_quantity
            > beer_presentation.current_stock
        ):
            raise InsufficientBeerPresentationStockError(
                "There is not enough bottle stock "
                "for this pasteurization."
            )

        waste_quantity = (
            pasteurization_data.processed_quantity
            - pasteurization_data.approved_quantity
        )

        try:
            code = generate_code(
                db,
                "bottle_pasteurization_run",
            )

            pasteurization_run = (
                create_bottle_pasteurization_run(
                    db,
                    code=code,
                    beer_presentation_id=beer_presentation.id,
                    processed_quantity=(
                        pasteurization_data.processed_quantity
                    ),
                    approved_quantity=(
                        pasteurization_data.approved_quantity
                    ),
                    waste_quantity=waste_quantity,
                    performed_by_user_id=(
                        current_user.id
                        if current_user is not None
                        else None
                    ),
                    notes=pasteurization_data.notes,
                    occurred_at=pasteurization_data.occurred_at,
                )
            )

            if waste_quantity > 0:
                create_pasteurization_waste_movement(
                    db,
                    beer_presentation_id=beer_presentation.id,
                    pasteurization_run_id=pasteurization_run.id,
                    quantity=waste_quantity,
                    reference=code,
                    notes=(
                        "Bottle waste from pasteurization "
                        f"{code}."
                    ),
                )

                update_beer_presentation_stock(
                    db,
                    beer_presentation,
                    (
                        beer_presentation.current_stock
                        - waste_quantity
                    ),
                )

            db.commit()

        except Exception:
            db.rollback()
            raise

        db.refresh(pasteurization_run)

        return pasteurization_run