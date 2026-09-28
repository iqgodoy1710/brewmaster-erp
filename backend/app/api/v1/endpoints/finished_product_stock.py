from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.finished_product_stock import (
    BeerKegStockCoverageResponse,
    KegFinishedProductStockResponse,
    PackagedFinishedProductStockResponse,
)
from app.schemas.stock_coverage_requirement import (
    StockCoveragePlanResponse,
)
from app.services.finished_product_stock_service import (
    FinishedProductStockService,
)
from app.services.stock_coverage_service import (
    StockCoverageService,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/finished-product-stock",
    tags=["Finished Product Stock"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.OPERATOR,
                UserRole.MANAGEMENT,
            )
        )
    ],
)


@router.get(
    "/kegs",
    response_model=list[KegFinishedProductStockResponse],
)
def read_keg_finished_product_stock(
    db: Session = Depends(get_db),
):
    return FinishedProductStockService.get_kegs(db)


@router.get(
    "/packaged",
    response_model=list[PackagedFinishedProductStockResponse],
)
def read_packaged_finished_product_stock(
    db: Session = Depends(get_db),
):
    return FinishedProductStockService.get_packaged(db)

@router.get(
    "/keg-coverage",
    response_model=list[BeerKegStockCoverageResponse],
)
def read_beer_keg_stock_coverage(
    db: Session = Depends(get_db),
):
    return FinishedProductStockService.get_keg_coverage(db)

@router.get(
    "/raw-material-requirements",
    response_model=StockCoveragePlanResponse,
)
def read_raw_material_coverage_requirements(
    db: Session = Depends(get_db),
):
    return StockCoverageService.get_raw_material_plan(db)