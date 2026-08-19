from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.sale_item import SaleItemCreate, SaleItemResponse
from app.services.sale_item_service import SaleItemService
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Sale Items"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)


@router.get(
    "/sales/{sale_id}/items",
    response_model=list[SaleItemResponse],
)
def read_sale_items(
    sale_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return SaleItemService.get_all_by_sale(db, sale_id)


@router.post(
    "/sale-items/",
    response_model=SaleItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sale_item(
    sale_item: SaleItemCreate,
    db: Session = Depends(get_db),
):
    return SaleItemService.create(db, sale_item)
