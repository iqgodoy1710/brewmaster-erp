from app.common.exceptions import (
    PackagingFormatCodeAlreadyExistsError,
    PackagingFormatNameAlreadyExistsError,
)
from app.crud.packaging_format import (
    create_packaging_format,
    get_packaging_format_by_code,
    get_packaging_format_by_name,
    get_packaging_formats,
)
from app.schemas.packaging_format import PackagingFormatCreate
from sqlalchemy.orm import Session


class PackagingFormatService:
    @staticmethod
    def get_all(db: Session):
        return get_packaging_formats(db)

    @staticmethod
    def create(
        db: Session,
        packaging_format_data: PackagingFormatCreate,
    ):
        existing_format_by_code = get_packaging_format_by_code(
            db,
            packaging_format_data.code,
        )
        if existing_format_by_code:
            raise PackagingFormatCodeAlreadyExistsError(
                "A packaging format with this code already exists."
            )

        existing_format_by_name = get_packaging_format_by_name(
            db,
            packaging_format_data.name,
        )
        if existing_format_by_name:
            raise PackagingFormatNameAlreadyExistsError(
                "A packaging format with this name already exists."
            )

        return create_packaging_format(db, packaging_format_data)