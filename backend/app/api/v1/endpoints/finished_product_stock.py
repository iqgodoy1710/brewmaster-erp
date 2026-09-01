from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.finished_product_stock import (
    KegFinishedProductStockResponse,
    PackagedFinishedProductStockResponse,
)
from app.services.finished_product_stock_service import (
    FinishedProductStockService,
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