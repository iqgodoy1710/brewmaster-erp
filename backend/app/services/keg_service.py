from app.common.exceptions import (
    InactivePackagingFormatError,
    InvalidKegPackagingFormatError,
    KegCodeAlreadyExistsError,
    KegNotFoundError,
    PackagingFormatNotFoundError,
)
from app.crud.keg import (
    create_keg,
    get_keg_by_code,
    get_kegs,
)
from app.crud.packaging_format import get_packaging_format_by_id
from app.models.enums import PackagingFormatType
from app.schemas.keg import KegCreate
from sqlalchemy.orm import Session


class KegService:
    @staticmethod
    def get_all(db: Session):
        return get_kegs(db)

    @staticmethod
    def create(
        db: Session,
        keg_data: KegCreate,
    ):
        normalized_code = keg_data.code.strip().upper()

        existing_keg = get_keg_by_code(
            db,
            normalized_code,
        )
        if existing_keg:
            raise KegCodeAlreadyExistsError(
                "A keg with this code already exists."
            )

        packaging_format = get_packaging_format_by_id(
            db,
            keg_data.packaging_format_id,
        )
        if not packaging_format:
            raise PackagingFormatNotFoundError(
                "The packaging format does not exist."
            )

        if not packaging_format.active:
            raise InactivePackagingFormatError(
                "Cannot register a keg for an inactive packaging format."
            )

        if packaging_format.format_type != PackagingFormatType.KEG:
            raise InvalidKegPackagingFormatError(
                "A keg must use a packaging format of type keg."
            )

        return create_keg(
            db,
            keg_data,
            normalized_code,
        )

    @staticmethod
    def get_by_code(
        db: Session,
        code: str,
    ):
        keg = get_keg_by_code(
            db,
            code.strip().upper(),
        )

        if not keg or not keg.active:
            raise KegNotFoundError("The keg does not exist.")

        return keg