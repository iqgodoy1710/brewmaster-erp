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


class BeerPresentationStockMovementType(StrEnum):
    PACKAGING_RECEIPT = "packaging_receipt"
    SALE = "sale"
    INITIAL_BALANCE = "initial_balance"
    WASTE = "waste"
    EXPIRATION = "expiration"
    INVENTORY_ADJUSTMENT_IN = "inventory_adjustment_in"
    INVENTORY_ADJUSTMENT_OUT = "inventory_adjustment_out"


class SaleStatus(StrEnum):
    DRAFT = "draft"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UserRole(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    MANAGEMENT = "management"


class CustomerPaymentMethod(StrEnum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    OTHER = "other"


class CustomerAccountMovementType(StrEnum):
    SALE_CHARGE = "sale_charge"
    PAYMENT = "payment"
    SALE_CANCELLATION = "sale_cancellation"


class PackagingFormatType(StrEnum):
    BOTTLE = "bottle"
    KEG = "keg"
    CAN = "can"
    OTHER = "other"


class KegFormFactor(StrEnum):
    STANDARD = "standard"
    FLAT = "flat"
    SLIM = "slim"


class KegStatus(StrEnum):
    CLEAN_AVAILABLE = "clean_available"
    DIRTY = "dirty"
    FILLED = "filled"
    AT_CUSTOMER = "at_customer"
    TAPPED = "tapped"
    OUT_OF_SERVICE = "out_of_service"


class KegMovementType(StrEnum):
    FILLING = "filling"
    DELIVERY = "delivery"
    RETURN = "return"
    WASHING = "washing"
    TAPPING = "tapping"
    REMNANT_TRANSFER = "remnant_transfer"
    INVENTORY_ADJUSTMENT = "inventory_adjustment"
    OUT_OF_SERVICE = "out_of_service"
