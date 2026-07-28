from decimal import Decimal

from app.common.exceptions import (
    InsufficientStockError,
    InvalidStockMovementError,
    RawMaterialNotFoundError,
    SupplierNotFoundError,
)
from app.crud.raw_material import (
    get_raw_material_by_id,
    update_raw_material_stock,
)
from app.crud.raw_material_stock_movement import (
    create_raw_material_stock_movement, get_raw_material_stock_movements
)
from app.crud.supplier import get_supplier_by_id
from app.models.enums import RawMaterialMovementType
from app.schemas.raw_material_stock_movement import (
    RawMaterialStockMovementCreate,
)
from sqlalchemy.orm import Session


class RawMaterialStockMovementService:
    @staticmethod
    def create(
        db: Session,
        movement_data: RawMaterialStockMovementCreate,
    ):
        raw_material = get_raw_material_by_id(
            db,
            movement_data.raw_material_id,
        )
        if not raw_material:
            raise RawMaterialNotFoundError(
                "The raw material does not exist."
            )

        if not raw_material.active:
            raise InvalidStockMovementError(
                "Cannot register a movement for an inactive raw material."
            )

        RawMaterialStockMovementService._validate_supplier(
            db,
            movement_data,
        )

        stock_change = (
            RawMaterialStockMovementService._get_stock_change(
                movement_data.movement_type,
                movement_data.quantity,
            )
        )

        new_stock = raw_material.current_stock + stock_change

        if new_stock < 0:
            raise InsufficientStockError(
                "There is not enough stock for this movement."
            )

        try:
            movement = create_raw_material_stock_movement(
                db,
                movement_data,
            )
            update_raw_material_stock(
                db,
                raw_material,
                new_stock,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(movement)

        return movement

    @staticmethod
    def _validate_supplier(
        db: Session,
        movement_data: RawMaterialStockMovementCreate,
    ) -> None:
        is_purchase_receipt = (
            movement_data.movement_type
            == RawMaterialMovementType.PURCHASE_RECEIPT
        )

        if is_purchase_receipt:
            if movement_data.supplier_id is None:
                raise InvalidStockMovementError(
                    "Purchase receipts require a supplier."
                )

            if movement_data.unit_cost is None:
                raise InvalidStockMovementError(
                    "Purchase receipts require a unit cost."
                )

            supplier = get_supplier_by_id(
                db,
                movement_data.supplier_id,
            )
            if not supplier:
                raise SupplierNotFoundError(
                    "The supplier does not exist."
                )

        elif movement_data.supplier_id is not None:
            raise InvalidStockMovementError(
                "Only purchase receipts can have a supplier."
            )

    @staticmethod
    def _get_stock_change(
        movement_type: RawMaterialMovementType,
        quantity: Decimal,
    ) -> Decimal:
        inbound_movement_types = {
            RawMaterialMovementType.PURCHASE_RECEIPT,
            RawMaterialMovementType.INITIAL_BALANCE,
            RawMaterialMovementType.INVENTORY_ADJUSTMENT_IN,
        }

        outbound_movement_types = {
            RawMaterialMovementType.PRODUCTION_CONSUMPTION,
            RawMaterialMovementType.WASTE,
            RawMaterialMovementType.EXPIRATION,
            RawMaterialMovementType.INVENTORY_ADJUSTMENT_OUT,
        }

        if movement_type in inbound_movement_types:
            return quantity

        if movement_type in outbound_movement_types:
            return -quantity

        raise InvalidStockMovementError(
            "The movement type is not valid."
        )

    @staticmethod
    def get_all_by_raw_material(
        db: Session,
        raw_material_id: int,
    ):
        raw_material = get_raw_material_by_id(
            db,
            raw_material_id,
        )
        if not raw_material:
            raise RawMaterialNotFoundError(
                "The raw material does not exist."
            )

        return get_raw_material_stock_movements(
            db,
            raw_material_id,
        )