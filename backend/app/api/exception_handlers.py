from app.common.exceptions import (
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    RawMaterialCodeAlreadyExistsError,
    RawMaterialNotFoundError,
    SupplierNameAlreadyExistsError,
    SupplierTaxIdAlreadyExistsError,
    UnitNameAlreadyExistsError,
    UnitNotFoundError,
    UnitSymbolAlreadyExistsError,
)
from fastapi import Request
from fastapi.responses import JSONResponse


async def raw_material_code_already_exists_handler(
    request: Request,
    error: RawMaterialCodeAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def related_resource_not_found_handler(
    request: Request,
    error: CategoryNotFoundError | UnitNotFoundError | RawMaterialNotFoundError ,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(error)},
    )

async def category_name_already_exists_handler(
    request: Request,
    error: CategoryNameAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )

async def unit_already_exists_handler(
    request: Request,
    error: UnitNameAlreadyExistsError | UnitSymbolAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )

async def supplier_already_exists_handler(
        request: Request,
        error: SupplierNameAlreadyExistsError | SupplierTaxIdAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)}
    )
