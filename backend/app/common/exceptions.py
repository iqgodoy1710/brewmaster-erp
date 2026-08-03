#Excepciones relacionadas a RAW MATERIALS

class RawMaterialCodeAlreadyExistsError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class UnitNotFoundError(Exception):
    pass

class RawMaterialNotFoundError(Exception):
    pass

#Excepciones relacionadas a CATEGORIAS
class CategoryNameAlreadyExistsError(Exception):
    pass


#Excepciones relacionadas a UNITS
class UnitNameAlreadyExistsError(Exception):
    pass

class UnitSymbolAlreadyExistsError(Exception):
    pass

#Excepciones relacionadas a SUPPLIERS
class SupplierNameAlreadyExistsError(Exception):
    pass

class SupplierTaxIdAlreadyExistsError(Exception):
    pass

#Excepciones relacionadas a RAW MATERIAL STOCK MOVEMENT
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