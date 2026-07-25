from fastapi import FastAPI

from app.api.exception_handlers import (
    category_name_already_exists_handler,
    raw_material_code_already_exists_handler,
    related_resource_not_found_handler,
    unit_already_exists_handler,
)
from app.api.v1.endpoints.categories import router as category_router
from app.api.v1.endpoints.raw_materials import router as raw_materials_router
from app.api.v1.endpoints.units import router as unit_router
from app.common.exceptions import (
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    RawMaterialCodeAlreadyExistsError,
    RawMaterialNotFoundError,
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


@app.get("/")
def home():
    return {"message": "Bienvenido a BrewMaster ERP"}


app.include_router(raw_materials_router)

app.include_router(category_router)

app.include_router(unit_router)