from app.common.exceptions import (
    BeerCodeAlreadyExistsError,
    BeerNameAlreadyExistsError,
    BeerNotFoundError,
    BeerPresentationAlreadyExistsError,
    BeerPresentationCodeAlreadyExistsError,
    BeerPresentationHasNoPackagingMaterialsError,
    BeerPresentationNameAlreadyExistsError,
    BeerPresentationNotFoundError,
    BeerPresentationPackagingMaterialAlreadyExistsError,
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    InactiveBeerError,
    InactiveBeerPresentationError,
    InactivePackagingFormatError,
    InactiveRawMaterialError,
    InactiveRecipeError,
    InsufficientBeerPresentationStockError,
    InsufficientBulkBeerError,
    InsufficientStockError,
    InvalidBeerPresentationStockMovementError,
    InvalidPackagingRunError,
    InvalidProductionBatchStatusError,
    InvalidStockMovementError,
    PackagingFormatCodeAlreadyExistsError,
    PackagingFormatNameAlreadyExistsError,
    PackagingFormatNotFoundError,
    PackagingRunCodeAlreadyExistsError,
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
    error: CategoryNotFoundError
    | UnitNotFoundError
    | RawMaterialNotFoundError
    | SupplierNotFoundError
    | BeerNotFoundError
    | RecipeNotFoundError
    | ProductionBatchNotFoundError
    | PackagingFormatNotFoundError
    | BeerPresentationNotFoundError,
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
    return JSONResponse(status_code=409, content={"detail": str(error)})


async def insufficient_stock_handler(
    request: Request,
    error: (
    InsufficientStockError
    | InsufficientBeerPresentationStockError
),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def invalid_stock_movement_handler(
    request: Request,
    error: (
    InvalidStockMovementError
    | InvalidBeerPresentationStockMovementError
),
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(error)},
    )


async def beer_already_exists_handler(
    request: Request,
    error: BeerCodeAlreadyExistsError | BeerNameAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def recipe_creation_conflict_handler(
    request: Request,
    error: InactiveBeerError | RecipeVersionAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def recipe_ingredient_conflict_handler(
    request: Request,
    error: (
        InactiveRawMaterialError
        | InactiveRecipeError
        | RecipeIngredientAlreadyExistsError
    ),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def production_batch_creation_conflict_handler(
    request: Request,
    error: (ProductionBatchCodeAlreadyExistsError | RecipeHasNoIngredientsError),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def production_batch_completion_conflict_handler(
    request: Request,
    error: InvalidProductionBatchStatusError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def packaging_format_already_exists_handler(
    request: Request,
    error: (
        PackagingFormatCodeAlreadyExistsError | PackagingFormatNameAlreadyExistsError
    ),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def beer_presentation_conflict_handler(
    request: Request,
    error: (
        InactivePackagingFormatError
        | BeerPresentationAlreadyExistsError
        | BeerPresentationCodeAlreadyExistsError
        | BeerPresentationNameAlreadyExistsError
    ),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def beer_presentation_packaging_material_conflict_handler(
    request: Request,
    error: (
        InactiveBeerPresentationError
        | BeerPresentationPackagingMaterialAlreadyExistsError
    ),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )

async def packaging_run_conflict_handler(
    request: Request,
    error: (
        PackagingRunCodeAlreadyExistsError
        | BeerPresentationHasNoPackagingMaterialsError
        | InvalidPackagingRunError
        | InsufficientBulkBeerError
    ),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )