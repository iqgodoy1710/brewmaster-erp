from app.common.exceptions import (
    PackagingFormatNameAlreadyExistsError,
)
from app.crud.packaging_format import (
    create_packaging_format,
    get_packaging_format_by_name,
    get_packaging_formats,
)
from app.schemas.packaging_format import PackagingFormatCreate
from app.services.code_service import generate_code
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
        existing_format_by_name = get_packaging_format_by_name(
            db,
            packaging_format_data.name,
        )
        if existing_format_by_name:
            raise PackagingFormatNameAlreadyExistsError(
                "A packaging format with this name already exists."
            )

        generated_code = generate_code(
            db,
            "packaging_format",
        )

        return create_packaging_format(
            db,
            packaging_format_data,
            generated_code,
        )