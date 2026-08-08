from app.db.dependencies import get_db
from app.schemas.sale import SaleCancel, SaleCreate, SaleResponse
from app.schemas.sale_detail import SaleDetailResponse
from app.services.sale_service import SaleService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.sale_report import SaleReportItemResponse


router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
)


@router.get("/", response_model=list[SaleResponse])
def read_sales(
    db: Session = Depends(get_db),
):
    return SaleService.get_all(db)


@router.get(
    "/report",
    response_model=list[SaleReportItemResponse],
)
def read_completed_sales_report(
    db: Session = Depends(get_db),
):
    return SaleService.get_completed_report(db)


@router.post(
    "/",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
):
    return SaleService.create(db, sale)


@router.get(
    "/{code}/detail",
    response_model=SaleDetailResponse,
)
def read_sale_detail(
    code: str,
    db: Session = Depends(get_db),
):
    return SaleService.get_detail(db, code)


@router.post(
    "/{code}/complete",
    response_model=SaleResponse,
)
def complete_sale(
    code: str,
    db: Session = Depends(get_db),
):
    return SaleService.complete(db, code)


@router.post(
    "/{code}/cancel",
    response_model=SaleResponse,
)
def cancel_sale(
    code: str,
    cancellation: SaleCancel,
    db: Session = Depends(get_db),
):
    return SaleService.cancel(
        db,
        code,
        cancellation,
    )
