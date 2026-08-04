from fastapi import FastAPI

from app.api.exception_handlers import (
    beer_already_exists_handler,
    beer_presentation_conflict_handler,
    category_name_already_exists_handler,
    insufficient_stock_handler,
    invalid_stock_movement_handler,
    packaging_format_already_exists_handler,
    production_batch_completion_conflict_handler,
    production_batch_creation_conflict_handler,
    raw_material_code_already_exists_handler,
    recipe_creation_conflict_handler,
    recipe_ingredient_conflict_handler,
    related_resource_not_found_handler,
    supplier_already_exists_handler,
    unit_already_exists_handler,
)
from app.api.v1.endpoints.beer_presentations import (
    router as beer_presentation_router,
)
from app.api.v1.endpoints.beers import router as beer_router
from app.api.v1.endpoints.categories import router as category_router
from app.api.v1.endpoints.packaging_formats import router as packaging_format_router
from app.api.v1.endpoints.production_batches import router as production_batch_router
from app.api.v1.endpoints.raw_material_stock_movements import (
    router as raw_material_stock_movements_router,
)
from app.api.v1.endpoints.raw_materials import router as raw_materials_router
from app.api.v1.endpoints.recipe_ingredients import router as recipe_ingredients_router
from app.api.v1.endpoints.recipes import router as recipe_router
from app.api.v1.endpoints.suppliers import router as supplier_router
from app.api.v1.endpoints.units import router as unit_router
from app.common.exceptions import (
    BeerCodeAlreadyExistsError,
    BeerNameAlreadyExistsError,
    BeerNotFoundError,
    BeerPresentationAlreadyExistsError,
    BeerPresentationCodeAlreadyExistsError,
    BeerPresentationNameAlreadyExistsError,
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    InactiveBeerError,
    InactivePackagingFormatError,
    InactiveRawMaterialError,
    InactiveRecipeError,
    InsufficientStockError,
    InvalidProductionBatchStatusError,
    InvalidStockMovementError,
    PackagingFormatCodeAlreadyExistsError,
    PackagingFormatNameAlreadyExistsError,
    PackagingFormatNotFoundError,
    ProductionBatchCodeAlreadyExistsError,
    ProductionBatchNotFoundError,
    RawMaterialCodeAlreadyExistsError,
    RawMaterialNotFoundError,
    RecipeHasNoIngredientsError,
    RecipeIngredientAlreadyExistsError,
    RecipeNotFoundError,
    RecipeVersionAlreadyExistsError,
    SupplierNameAlreadyExistsError,
    SupplierNotFoundError,
    SupplierTaxIdAlreadyExistsError,
    UnitNameAlreadyExistsError,
    UnitNotFoundError,
    UnitSymbolAlreadyExistsError,
)

app = FastAPI(title="BrewMaster ERP API", version="1.0.0")

app.add_exception_handler(
    RawMaterialCodeAlreadyExistsError,
    raw_material_code_already_exists_handler,
)
app.add_exception_handler(
    CategoryNotFoundError,
    related_resource_not_found_handler,
)
app.add_exception_handler(
    UnitNotFoundError,
    related_resource_not_found_handler,
)
app.add_exception_handler(RawMaterialNotFoundError, related_resource_not_found_handler)

app.add_exception_handler(
    CategoryNameAlreadyExistsError, category_name_already_exists_handler
)

app.add_exception_handler(UnitNameAlreadyExistsError, unit_already_exists_handler)

app.add_exception_handler(UnitSymbolAlreadyExistsError, unit_already_exists_handler)

app.add_exception_handler(
    SupplierNameAlreadyExistsError, supplier_already_exists_handler
)

app.add_exception_handler(
    SupplierTaxIdAlreadyExistsError, supplier_already_exists_handler
)

app.add_exception_handler(InsufficientStockError, insufficient_stock_handler)

app.add_exception_handler(InvalidStockMovementError, invalid_stock_movement_handler)

app.add_exception_handler(SupplierNotFoundError, related_resource_not_found_handler)

app.add_exception_handler(BeerCodeAlreadyExistsError, beer_already_exists_handler)

app.add_exception_handler(BeerNameAlreadyExistsError, beer_already_exists_handler)

app.add_exception_handler(
    RecipeVersionAlreadyExistsError, recipe_creation_conflict_handler
)

app.add_exception_handler(BeerNotFoundError, related_resource_not_found_handler)

app.add_exception_handler(InactiveBeerError, recipe_creation_conflict_handler)

app.add_exception_handler(
    RecipeNotFoundError,
    related_resource_not_found_handler,
)

app.add_exception_handler(
    InactiveRecipeError,
    recipe_ingredient_conflict_handler,
)

app.add_exception_handler(
    InactiveRawMaterialError,
    recipe_ingredient_conflict_handler,
)

app.add_exception_handler(
    RecipeIngredientAlreadyExistsError,
    recipe_ingredient_conflict_handler,
)

app.add_exception_handler(
    ProductionBatchCodeAlreadyExistsError,
    production_batch_creation_conflict_handler,
)

app.add_exception_handler(
    RecipeHasNoIngredientsError,
    production_batch_creation_conflict_handler,
)

app.add_exception_handler(
    ProductionBatchNotFoundError,
    related_resource_not_found_handler,
)

app.add_exception_handler(
    InvalidProductionBatchStatusError,
    production_batch_completion_conflict_handler,
)

app.add_exception_handler(
    PackagingFormatNameAlreadyExistsError,
    packaging_format_already_exists_handler,
)

app.add_exception_handler(
    PackagingFormatCodeAlreadyExistsError,
    packaging_format_already_exists_handler,
)

app.add_exception_handler(
    PackagingFormatNotFoundError,
    related_resource_not_found_handler,
)

app.add_exception_handler(
    InactivePackagingFormatError,
    beer_presentation_conflict_handler,
)

app.add_exception_handler(
    BeerPresentationCodeAlreadyExistsError,
    beer_presentation_conflict_handler,
)

app.add_exception_handler(
    BeerPresentationNameAlreadyExistsError,
    beer_presentation_conflict_handler,
)

app.add_exception_handler(
    BeerPresentationAlreadyExistsError,
    beer_presentation_conflict_handler,
)

@app.get("/")
def home():
    return {"message": "Bienvenido a BrewMaster ERP"}


app.include_router(raw_materials_router)

app.include_router(category_router)

app.include_router(unit_router)

app.include_router(supplier_router)

app.include_router(raw_material_stock_movements_router)

app.include_router(beer_router)

app.include_router(recipe_router)

app.include_router(recipe_ingredients_router)

app.include_router(production_batch_router)

app.include_router(packaging_format_router)

app.include_router(beer_presentation_router)