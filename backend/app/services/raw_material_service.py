from sqlalchemy.orm import Session

from app.crud.raw_material import (
    get_raw_materials,
    create_raw_material,
    get_raw_material_by_code,
    update_raw_material,
    deactivate_raw_material
)
from app.schemas.raw_material import RawMaterialCreate, RawMaterialUpdate

from app.crud.category import get_category_by_id
from app.crud.unit import get_unit_by_id

from app.common.exceptions import (
    UnitNotFoundError,
    CategoryNotFoundError,
    RawMaterialCodeAlreadyExistsError,
    RawMaterialNotFoundError,
)


class RawMaterialService:
    @staticmethod
    def get_all(db: Session):

        return get_raw_materials(db)

    @staticmethod
    def create(db: Session, raw_material_data: RawMaterialCreate):
        existing_raw_material = get_raw_material_by_code(
            db,
            raw_material_data.code,
        )
        if existing_raw_material:
            raise RawMaterialCodeAlreadyExistsError(
                "A raw material with this code already exists."
            )

        category = get_category_by_id(db, raw_material_data.category_id)
        if not category:
            raise CategoryNotFoundError("The selected category does not exist.")

        unit = get_unit_by_id(db, raw_material_data.unit_id)
        if not unit:
            raise UnitNotFoundError("The selected unit does not exist.")

        return create_raw_material(db, raw_material_data)

    @staticmethod
    def get_by_code(db: Session, code: str):
        raw_material = get_raw_material_by_code(db, code)

        if not raw_material:
            raise RawMaterialNotFoundError("The raw material does not exist.")

        return raw_material

    @staticmethod
    def update(
        db: Session,
        code: str,
        raw_material_data: RawMaterialUpdate,
    ):
        raw_material = RawMaterialService.get_by_code(db, code)

        update_data = raw_material_data.model_dump(exclude_unset=True)

        if "code" in update_data and update_data["code"] != raw_material.code:
            existing_raw_material = get_raw_material_by_code(
                db,
                update_data["code"],
            )
            if existing_raw_material:
                raise RawMaterialCodeAlreadyExistsError(
                    "A raw material with this code already exists."
                )

        if "category_id" in update_data:
            category = get_category_by_id(db, update_data["category_id"])
            if not category:
                raise CategoryNotFoundError("The selected category does not exist.")

        if "unit_id" in update_data:
            unit = get_unit_by_id(db, update_data["unit_id"])
            if not unit:
                raise UnitNotFoundError("The selected unit does not exist.")

        return update_raw_material(
            db,
            raw_material,
            raw_material_data,
        )

    @staticmethod
    def deactivate(db: Session, code: str):
        raw_material = RawMaterialService.get_by_code(db, code)

        return deactivate_raw_material(db, raw_material)