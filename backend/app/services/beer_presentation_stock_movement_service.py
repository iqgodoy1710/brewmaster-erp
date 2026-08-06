from app.common.exceptions import (
    BeerPresentationNotFoundError,
    InactiveBeerPresentationError,
    InsufficientBeerPresentationStockError,
    InvalidBeerPresentationStockMovementError,
)
from app.crud.beer_presentation import (
    get_beer_presentation_by_id,
    update_beer_presentation_stock,
)
from app.crud.beer_presentation_stock_movement import (
    create_beer_presentation_stock_movement,
    get_beer_presentation_stock_movements,
)
from app.models.enums import BeerPresentationStockMovementType
from app.schemas.beer_presentation_stock_movement import (
    BeerPresentationStockMovementCreate,
)
from sqlalchemy.orm import Session


class BeerPresentationStockMovementService:
    @staticmethod
    def get_all_by_beer_presentation(
        db: Session,
        beer_presentation_id: int,
    ):
        beer_presentation = get_beer_presentation_by_id(
            db,
            beer_presentation_id,
        )
        if not beer_presentation:
            raise BeerPresentationNotFoundError(
                "The beer presentation does not exist."
            )

        return get_beer_presentation_stock_movements(
            db,
            beer_presentation_id,
        )

    @staticmethod
    def create(
        db: Session,
        movement_data: BeerPresentationStockMovementCreate,
    ):
        beer_presentation = get_beer_presentation_by_id(
            db,
            movement_data.beer_presentation_id,
        )
        if not beer_presentation:
            raise BeerPresentationNotFoundError(
                "The beer presentation does not exist."
            )

        if not beer_presentation.active:
            raise InactiveBeerPresentationError(
                "Cannot register a movement for an inactive beer presentation."
            )

        BeerPresentationStockMovementService._validate_manual_movement_type(
            movement_data.movement_type,
        )

        stock_change = (
            BeerPresentationStockMovementService._get_stock_change(
                movement_data.movement_type,
                movement_data.quantity,
            )
        )
        new_stock = beer_presentation.current_stock + stock_change

        if new_stock < 0:
            raise InsufficientBeerPresentationStockError(
                "There is not enough stock for this beer presentation."
            )

        try:
            movement = create_beer_presentation_stock_movement(
                db,
                movement_data,
            )
            update_beer_presentation_stock(
                db,
                beer_presentation,
                new_stock,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(movement)

        return movement

    @staticmethod
    def _validate_manual_movement_type(
        movement_type: BeerPresentationStockMovementType,
    ) -> None:
        if (
            movement_type
            == BeerPresentationStockMovementType.PACKAGING_RECEIPT
        ):
            raise InvalidBeerPresentationStockMovementError(
                "Packaging receipts must be registered by a packaging run."
            )

    @staticmethod
    def _get_stock_change(
        movement_type: BeerPresentationStockMovementType,
        quantity: int,
    ) -> int:
        inbound_movement_types = {
            BeerPresentationStockMovementType.INITIAL_BALANCE,
            BeerPresentationStockMovementType.INVENTORY_ADJUSTMENT_IN,
        }

        outbound_movement_types = {
            BeerPresentationStockMovementType.SALE,
            BeerPresentationStockMovementType.WASTE,
            BeerPresentationStockMovementType.EXPIRATION,
            BeerPresentationStockMovementType.INVENTORY_ADJUSTMENT_OUT,
        }

        if movement_type in inbound_movement_types:
            return quantity

        if movement_type in outbound_movement_types:
            return -quantity

        raise InvalidBeerPresentationStockMovementError(
            "The movement type is not valid."
        )