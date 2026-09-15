from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.packaging_format import (
    PackagingFormatCreate,
    PackagingFormatResponse,
)
from app.services.packaging_format_service import PackagingFormatService
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/packaging-formats",
    tags=["Packaging Formats"],
)


@router.get(
    "/",
    response_model=list[PackagingFormatResponse],
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
def read_packaging_formats(
    db: Session = Depends(get_db),
):
    return PackagingFormatService.get_all(db)


@router.post(
    "/",
    response_model=PackagingFormatResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def create_packaging_format(
    packaging_format: PackagingFormatCreate,
    db: Session = Depends(get_db),
):
    return PackagingFormatService.create(db, packaging_format)
