from enum import StrEnum


class RawMaterialMovementType(StrEnum):
    PURCHASE_RECEIPT = "purchase_receipt"
    PRODUCTION_CONSUMPTION = "production_consumption"
    INITIAL_BALANCE = "initial_balance"
    WASTE = "waste"
    EXPIRATION = "expiration"
    INVENTORY_ADJUSTMENT_IN = "inventory_adjustment_in"
    INVENTORY_ADJUSTMENT_OUT = "inventory_adjustment_out"

class ProductionBatchStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"