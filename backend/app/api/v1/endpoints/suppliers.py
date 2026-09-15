import app.models
from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.supplier import SupplierCreate, SupplierResponse
from app.services.supplier_service import SupplierService
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],

)


@router.get(
    "/",
    response_model=list[SupplierResponse],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
                UserRole.OPERATOR,
            )
        )
    ],
)
def read_suppliers(db: Session = Depends(get_db)):
    return SupplierService.get_all(db)


@router.post(
    "/",
    response_model=SupplierResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
):
    return SupplierService.create(db, supplier)
