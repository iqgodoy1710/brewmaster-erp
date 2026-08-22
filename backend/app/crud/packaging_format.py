from sqlalchemy.orm import Session

from app.models.packaging_format import PackagingFormat
from app.schemas.packaging_format import PackagingFormatCreate


def get_packaging_formats(
    db: Session,
) -> list[PackagingFormat]:
    return db.query(PackagingFormat).filter(PackagingFormat.active.is_(True)).all()


def get_packaging_format_by_code(
    db: Session,
    code: str,
) -> PackagingFormat | None:
    return db.query(PackagingFormat).filter(PackagingFormat.code == code).first()


def get_packaging_format_by_name(
    db: Session,
    name: str,
) -> PackagingFormat | None:
    return db.query(PackagingFormat).filter(PackagingFormat.name == name).first()


def create_packaging_format(
    db: Session,
    packaging_format_data: PackagingFormatCreate,
    code: str,
) -> PackagingFormat:
    packaging_format = PackagingFormat(
        code=code,
        **packaging_format_data.model_dump(),
    )

    db.add(packaging_format)
    db.commit()
    db.refresh(packaging_format)

    return packaging_format


def get_packaging_format_by_id(
    db: Session,
    packaging_format_id: int,
) -> PackagingFormat | None:
    return (
        db.query(PackagingFormat)
        .filter(PackagingFormat.id == packaging_format_id)
        .first()
    )
