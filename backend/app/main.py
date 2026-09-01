import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.exception_handlers import (
    beer_already_exists_handler,
    beer_presentation_conflict_handler,
    beer_presentation_packaging_material_conflict_handler,
    category_name_already_exists_handler,
    cost_estimate_conflict_handler,
    customer_already_exists_handler,
    delivery_order_conflict_handler,
    insufficient_permissions_handler,
    insufficient_stock_handler,
    invalid_credentials_handler,
    invalid_stock_movement_handler,
    invalid_user_update_handler,
    keg_conflict_handler,
    keg_not_found_handler,
    packaging_format_already_exists_handler,
    packaging_run_conflict_handler,
    production_batch_completion_conflict_handler,
    production_batch_creation_conflict_handler,
    raw_material_code_already_exists_handler,
    recipe_creation_conflict_handler,
    recipe_ingredient_conflict_handler,
    related_resource_not_found_handler,
    sale_conflict_handler,
    supplier_already_exists_handler,
    unit_already_exists_handler,
    user_already_exists_handler,
)
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.beer_presentation_cost_estimates import (
    router as beer_presentation_cost_estimate_router,
)
from app.api.v1.endpoints.beer_presentation_packaging_materials import (
    router as beer_presentation_packaging_material_router,
)
from app.api.v1.endpoints.beer_presentation_prices import (
    router as beer_presentation_price_router,
)
from app.api.v1.endpoints.beer_presentation_stock_movements import (
    router as beer_presentation_stock_movement_router,
)
from app.api.v1.endpoints.beer_presentations import (
    router as beer_presentation_router,
)
from app.api.v1.endpoints.beers import router as beer_router
from app.api.v1.endpoints.categories import router as category_router
from app.api.v1.endpoints.customer_accounts import (
    router as customer_account_router,
)
from app.api.v1.endpoints.customers import router as customer_router
from app.api.v1.endpoints.delivery_orders import (
    router as delivery_order_router,
)
from app.api.v1.endpoints.finished_product_stock import (
    router as finished_product_stock_router,
)
from app.api.v1.endpoints.keg_movements import (
    router as keg_movements_router,
)
from app.api.v1.endpoints.keg_repackaging_runs import (
    router as keg_repackaging_runs_router,
)
from app.api.v1.endpoints.kegs import router as kegs_router
from app.api.v1.endpoints.packaging_formats import router as packaging_format_router
from app.api.v1.endpoints.packaging_runs import (
    router as packaging_run_router,
)
from app.api.v1.endpoints.production_batches import router as production_batch_router
from app.api.v1.endpoints.raw_material_stock_movements import (
    router as raw_material_stock_movements_router,
)
from app.api.v1.endpoints.raw_materials import router as raw_materials_router
from app.api.v1.endpoints.recipe_ingredients import router as recipe_ingredients_router
from app.api.v1.endpoints.recipes import router as recipe_router
from app.api.v1.endpoints.sale_items import router as sale_item_router
from app.api.v1.endpoints.sales import router as sale_router
from app.api.v1.endpoints.suppliers import router as supplier_router
from app.api.v1.endpoints.units import router as unit_router
from app.api.v1.endpoints.users import router as user_router
from app.common.exceptions import (
    BeerCodeAlreadyExistsError,
    BeerNameAlreadyExistsError,
    BeerNotFoundError,
    BeerPresentationAlreadyExistsError,
    BeerPresentationCodeAlreadyExistsError,
    BeerPresentationHasNoActivePriceError,
    BeerPresentationHasNoPackagingMaterialsError,
    BeerPresentationNameAlreadyExistsError,
    BeerPresentationNotFoundError,
    BeerPresentationPackagingMaterialAlreadyExistsError,
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    CustomerCodeAlreadyExistsError,
    CustomerNotFoundError,
    CustomerTaxIdAlreadyExistsError,
    DeliveryOrderHasNoItemsError,
    DeliveryOrderItemAlreadyExistsError,
    DeliveryOrderItemNotFoundError,
    DeliveryOrderKegAlreadyExistsError,
    DeliveryOrderNotFoundError,
    InactiveBeerError,
    InactiveBeerPresentationError,
    InactiveCustomerError,
    InactiveKegError,
    InactivePackagingFormatError,
    InactiveRawMaterialError,
    InactiveRecipeError,
    InsufficientBeerPresentationStockError,
    InsufficientBulkBeerError,
    InsufficientPermissionsError,
    InsufficientStockError,
    InvalidBeerPresentationCostEstimateError,
    InvalidBeerPresentationStockMovementError,
    InvalidCredentialsError,
    InvalidDeliveryOrderCloseError,
    InvalidDeliveryOrderItemError,
    InvalidDeliveryOrderKegError,
    InvalidDeliveryOrderStatusError,
    InvalidKegDeliveryError,
    InvalidKegFillingError,
    InvalidKegPackagingFormatError,
    InvalidKegRemnantTransferError,
    InvalidKegRepackagingError,
    InvalidKegReturnError,
    InvalidKegWashingError,
    InvalidPackagingRunError,
    InvalidProductionBatchStatusError,
    InvalidSaleStatusError,
    InvalidStockMovementError,
    InvalidUserUpdateError,
    KegCodeAlreadyExistsError,
    KegNotFoundError,
    KegPresentationCannotHavePackagingMaterialsError,
    PackagingFormatCodeAlreadyExistsError,
    PackagingFormatNameAlreadyExistsError,
    PackagingFormatNotFoundError,
    PackagingRunCodeAlreadyExistsError,
    ProductionBatchCodeAlreadyExistsError,
    ProductionBatchNotFoundError,
    RawMaterialCodeAlreadyExistsError,
    RawMaterialNotFoundError,
    RecipeHasNoIngredientsError,
    RecipeHasProductionBatchesError,
    RecipeIngredientAlreadyExistsError,
    RecipeIngredientNotFoundError,
    RecipeNotFoundError,
    RecipeVersionAlreadyExistsError,
    SaleCodeAlreadyExistsError,
    SaleHasNoItemsError,
    SaleItemAlreadyExistsError,
    SaleNotFoundError,
    SupplierNameAlreadyExistsError,
    SupplierNotFoundError,
    SupplierTaxIdAlreadyExistsError,
    UnitNameAlreadyExistsError,
    UnitNotFoundError,
    UnitSymbolAlreadyExistsError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)

app = FastAPI(title="BrewMaster ERP API", version="1.0.0")


@app.middleware("http")
async def block_demo_writes(request: Request, call_next):
    is_demo_read_only = os.getenv("DEMO_READ_ONLY") == "true"

    if is_demo_read_only and request.method not in {"GET", "HEAD", "OPTIONS"}:
        return JSONResponse(
            status_code=403,
            content={"detail": "This public demo is read-only."},
        )

    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://brewmaster-erp-demo.onrender.com",
        "https://brewmaster-erp-beta.onrender.com",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.add_exception_handler(
    BeerPresentationNotFoundError,
    related_resource_not_found_handler,
)

app.add_exception_handler(
    InactiveBeerPresentationError,
    beer_presentation_packaging_material_conflict_handler,
)

app.add_exception_handler(
    BeerPresentationPackagingMaterialAlreadyExistsError,
    beer_presentation_packaging_material_conflict_handler,
)

app.add_exception_handler(
    PackagingRunCodeAlreadyExistsError,
    packaging_run_conflict_handler,
)

app.add_exception_handler(
    BeerPresentationHasNoPackagingMaterialsError,
    packaging_run_conflict_handler,
)

app.add_exception_handler(
    InvalidPackagingRunError,
    packaging_run_conflict_handler,
)

app.add_exception_handler(
    InsufficientBulkBeerError,
    packaging_run_conflict_handler,
)

app.add_exception_handler(
    InsufficientBeerPresentationStockError,
    insufficient_stock_handler,
)

app.add_exception_handler(
    InvalidBeerPresentationStockMovementError,
    invalid_stock_movement_handler,
)

app.add_exception_handler(
    CustomerCodeAlreadyExistsError,
    customer_already_exists_handler,
)

app.add_exception_handler(
    CustomerTaxIdAlreadyExistsError,
    customer_already_exists_handler,
)
app.add_exception_handler(
    CustomerNotFoundError,
    related_resource_not_found_handler,
)

app.add_exception_handler(
    SaleNotFoundError,
    related_resource_not_found_handler,
)

app.add_exception_handler(
    InactiveCustomerError,
    sale_conflict_handler,
)

app.add_exception_handler(
    SaleCodeAlreadyExistsError,
    sale_conflict_handler,
)

app.add_exception_handler(
    InvalidSaleStatusError,
    sale_conflict_handler,
)

app.add_exception_handler(
    SaleHasNoItemsError,
    sale_conflict_handler,
)

app.add_exception_handler(
    SaleItemAlreadyExistsError,
    sale_conflict_handler,
)

app.add_exception_handler(
    InvalidCredentialsError,
    invalid_credentials_handler,
)

app.add_exception_handler(
    InsufficientPermissionsError,
    insufficient_permissions_handler,
)

app.add_exception_handler(
    UsernameAlreadyExistsError,
    user_already_exists_handler,
)

app.add_exception_handler(
    UserNotFoundError,
    related_resource_not_found_handler,
)

app.add_exception_handler(
    InvalidUserUpdateError,
    invalid_user_update_handler,
)

app.add_exception_handler(
    BeerPresentationHasNoActivePriceError,
    sale_conflict_handler,
)

app.add_exception_handler(
    InvalidBeerPresentationCostEstimateError,
    cost_estimate_conflict_handler,
)

app.add_exception_handler(
    KegCodeAlreadyExistsError,
    keg_conflict_handler,
)

app.add_exception_handler(
    InvalidKegPackagingFormatError,
    keg_conflict_handler,
)

app.add_exception_handler(
    KegNotFoundError,
    keg_not_found_handler,
)

app.add_exception_handler(
    InactiveKegError,
    keg_conflict_handler,
)

app.add_exception_handler(
    InvalidKegFillingError,
    keg_conflict_handler,
)

app.add_exception_handler(
    InvalidKegDeliveryError,
    keg_conflict_handler,
)

app.add_exception_handler(
    InvalidKegReturnError,
    keg_conflict_handler,
)

app.add_exception_handler(
    InvalidKegWashingError,
    keg_conflict_handler,
)

app.add_exception_handler(
    InvalidKegRemnantTransferError,
    keg_conflict_handler,
)

app.add_exception_handler(
    RecipeIngredientNotFoundError,
    related_resource_not_found_handler,
)

app.add_exception_handler(
    RecipeHasProductionBatchesError,
    recipe_creation_conflict_handler,
)

app.add_exception_handler(
    InvalidKegRepackagingError,
    keg_conflict_handler,
)

app.add_exception_handler(
    KegPresentationCannotHavePackagingMaterialsError,
    beer_presentation_packaging_material_conflict_handler,
)

app.add_exception_handler(
    DeliveryOrderNotFoundError, related_resource_not_found_handler
)

app.add_exception_handler(
    DeliveryOrderItemNotFoundError, related_resource_not_found_handler
)

app.add_exception_handler(
    DeliveryOrderNotFoundError,
    related_resource_not_found_handler,
)
app.add_exception_handler(
    DeliveryOrderItemNotFoundError,
    related_resource_not_found_handler,
)

for exception_type in (
    DeliveryOrderItemAlreadyExistsError,
    DeliveryOrderKegAlreadyExistsError,
    DeliveryOrderHasNoItemsError,
    InvalidDeliveryOrderStatusError,
    InvalidDeliveryOrderItemError,
    InvalidDeliveryOrderKegError,
    InvalidDeliveryOrderCloseError,
):
    app.add_exception_handler(
        exception_type,
        delivery_order_conflict_handler,
    )

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


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

app.include_router(beer_presentation_packaging_material_router)

app.include_router(packaging_run_router)

app.include_router(beer_presentation_stock_movement_router)

app.include_router(customer_router)

app.include_router(sale_router)

app.include_router(sale_item_router)

app.include_router(auth_router)

app.include_router(user_router)

app.include_router(beer_presentation_price_router)

app.include_router(beer_presentation_cost_estimate_router)

app.include_router(customer_account_router)

app.include_router(kegs_router)

app.include_router(keg_movements_router)

app.include_router(keg_repackaging_runs_router)

app.include_router(finished_product_stock_router)

app.include_router(delivery_order_router)