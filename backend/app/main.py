from fastapi import FastAPI

from app.api.exception_handlers import (
    beer_already_exists_handler,
    category_name_already_exists_handler,
    insufficient_stock_handler,
    invalid_stock_movement_handler,
    raw_material_code_already_exists_handler,
    related_resource_not_found_handler,
    supplier_already_exists_handler,
    unit_already_exists_handler,
)
from app.api.v1.endpoints.beers import router as beer_router
from app.api.v1.endpoints.categories import router as category_router
from app.api.v1.endpoints.raw_material_stock_movements import (
    router as raw_material_stock_movements_router,
)
from app.api.v1.endpoints.raw_materials import router as raw_materials_router
from app.api.v1.endpoints.suppliers import router as supplier_router
from app.api.v1.endpoints.units import router as unit_router
from app.common.exceptions import (
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    InsufficientStockError,
    InvalidStockMovementError,
    RawMaterialCodeAlreadyExistsError,
    RawMaterialNotFoundError,
    SupplierNameAlreadyExistsError,
    SupplierNotFoundError,
    SupplierTaxIdAlreadyExistsError,
    UnitNameAlreadyExistsError,
    UnitNotFoundError,
    UnitSymbolAlreadyExistsError,
    BeerNameAlreadyExistsError,
    BeerCodeAlreadyExistsError
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
app.add_exception_handler(
    RawMaterialNotFoundError,
    related_resource_not_found_handler)

app.add_exception_handler(
    CategoryNameAlreadyExistsError,
    category_name_already_exists_handler
)

app.add_exception_handler(
    UnitNameAlreadyExistsError,
    unit_already_exists_handler)

app.add_exception_handler(
    UnitSymbolAlreadyExistsError,
    unit_already_exists_handler
)

app.add_exception_handler(
    SupplierNameAlreadyExistsError,
    supplier_already_exists_handler
)

app.add_exception_handler(
    SupplierTaxIdAlreadyExistsError,
    supplier_already_exists_handler
)

app.add_exception_handler(
    InsufficientStockError,
    insufficient_stock_handler
)

app.add_exception_handler(
    InvalidStockMovementError,
    invalid_stock_movement_handler
)

app.add_exception_handler(
    SupplierNotFoundError,
    related_resource_not_found_handler
)

app.add_exception_handler(
    BeerCodeAlreadyExistsError,
    beer_already_exists_handler
)

app.add_exception_handler(
    BeerNameAlreadyExistsError,
    beer_already_exists_handler
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