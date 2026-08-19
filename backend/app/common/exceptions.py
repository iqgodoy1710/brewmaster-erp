# Excepciones relacionadas a RAW MATERIALS


class RawMaterialCodeAlreadyExistsError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class UnitNotFoundError(Exception):
    pass


class RawMaterialNotFoundError(Exception):
    pass


# Excepciones relacionadas a CATEGORIAS
class CategoryNameAlreadyExistsError(Exception):
    pass


# Excepciones relacionadas a UNITS
class UnitNameAlreadyExistsError(Exception):
    pass


class UnitSymbolAlreadyExistsError(Exception):
    pass


# Excepciones relacionadas a SUPPLIERS
class SupplierNameAlreadyExistsError(Exception):
    pass


class SupplierTaxIdAlreadyExistsError(Exception):
    pass


# Excepciones relacionadas a RAW MATERIAL STOCK MOVEMENT
class SupplierNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class InvalidStockMovementError(Exception):
    pass


# Exceptions related to BEERS
class BeerCodeAlreadyExistsError(Exception):
    pass


class BeerNameAlreadyExistsError(Exception):
    pass


# Exceptions related to RECIPES
class BeerNotFoundError(Exception):
    pass


class RecipeVersionAlreadyExistsError(Exception):
    pass


class InactiveBeerError(Exception):
    pass


# Exceptions related to RECIPE INGREDIENTS
class RecipeNotFoundError(Exception):
    pass


class InactiveRecipeError(Exception):
    pass


class InactiveRawMaterialError(Exception):
    pass


class RecipeIngredientAlreadyExistsError(Exception):
    pass


# Exceptions related to PRODUCTION BATCHES
class ProductionBatchCodeAlreadyExistsError(Exception):
    pass


class RecipeHasNoIngredientsError(Exception):
    pass


class ProductionBatchNotFoundError(Exception):
    pass


class InvalidProductionBatchStatusError(Exception):
    pass


# Exceptions related to PACKAGING FORMATS
class PackagingFormatCodeAlreadyExistsError(Exception):
    pass


class PackagingFormatNameAlreadyExistsError(Exception):
    pass


# Exceptions related to BEER PRESENTATIONS
class PackagingFormatNotFoundError(Exception):
    pass


class InactivePackagingFormatError(Exception):
    pass


class BeerPresentationCodeAlreadyExistsError(Exception):
    pass


class BeerPresentationNameAlreadyExistsError(Exception):
    pass


class BeerPresentationAlreadyExistsError(Exception):
    pass


# Exceptions related to BEER PRESENTATION PACKAGING MATERIALS
class BeerPresentationNotFoundError(Exception):
    pass


class InactiveBeerPresentationError(Exception):
    pass


class BeerPresentationPackagingMaterialAlreadyExistsError(Exception):
    pass


# Exceptions related to PACKAGING RUNS
class PackagingRunCodeAlreadyExistsError(Exception):
    pass


class BeerPresentationHasNoPackagingMaterialsError(Exception):
    pass


class InvalidPackagingRunError(Exception):
    pass


class InsufficientBulkBeerError(Exception):
    pass


# Exceptions related to BEER PRESENTATION STOCK MOVEMENTS
class InsufficientBeerPresentationStockError(Exception):
    pass


class InvalidBeerPresentationStockMovementError(Exception):
    pass


# Exceptions related to CUSTOMERS
class CustomerCodeAlreadyExistsError(Exception):
    pass


class CustomerTaxIdAlreadyExistsError(Exception):
    pass


# Exceptions related to SALES
class CustomerNotFoundError(Exception):
    pass


class InactiveCustomerError(Exception):
    pass


class SaleCodeAlreadyExistsError(Exception):
    pass


class SaleNotFoundError(Exception):
    pass


class InvalidSaleStatusError(Exception):
    pass


class SaleHasNoItemsError(Exception):
    pass


class SaleItemAlreadyExistsError(Exception):
    pass


# Exceptions related to USERS
class UserEmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InsufficientPermissionsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidUserUpdateError(Exception):
    pass
