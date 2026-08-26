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
    InvalidKegDeliveryError,
    InvalidKegFillingError,
    InvalidKegPackagingFormatError,
    InvalidKegRemnantTransferError,
    InvalidKegReturnError,
    InvalidKegWashingError,
    InvalidPackagingRunError,
    InvalidProductionBatchStatusError,
    InvalidSaleStatusError,
    InvalidStockMovementError,
    InvalidUserUpdateError,
    KegCodeAlreadyExistsError,
    KegNotFoundError,
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
    | BeerPresentationNotFoundError
    | CustomerNotFoundError
    | SaleNotFoundError
    | UserNotFoundError
    | RecipeIngredientNotFoundError,
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
    error: (InsufficientStockError | InsufficientBeerPresentationStockError),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def invalid_stock_movement_handler(
    request: Request,
    error: (InvalidStockMovementError | InvalidBeerPresentationStockMovementError),
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


async def customer_already_exists_handler(
    request: Request,
    error: (CustomerCodeAlreadyExistsError | CustomerTaxIdAlreadyExistsError),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def sale_conflict_handler(
    request: Request,
    error: (
        InactiveCustomerError
        | SaleCodeAlreadyExistsError
        | InvalidSaleStatusError
        | SaleHasNoItemsError
        | SaleItemAlreadyExistsError
        | BeerPresentationHasNoActivePriceError
    ),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def invalid_credentials_handler(
    request: Request,
    error: InvalidCredentialsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": str(error)},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def insufficient_permissions_handler(
    request: Request,
    error: InsufficientPermissionsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"detail": str(error)},
    )


async def user_already_exists_handler(
    request: Request,
    error: UsernameAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def invalid_user_update_handler(
    request: Request,
    error: InvalidUserUpdateError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def cost_estimate_conflict_handler(
    request: Request,
    error: InvalidBeerPresentationCostEstimateError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def keg_conflict_handler(
    request: Request,
    error: (
        KegCodeAlreadyExistsError
        | InvalidKegPackagingFormatError
        | InactiveKegError
        | InvalidKegFillingError
        | InvalidKegDeliveryError
        | InvalidKegReturnError
        | InvalidKegWashingError
        | InvalidKegRemnantTransferError
    ),
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def keg_not_found_handler(
    request: Request,
    error: KegNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(error)},
    )
