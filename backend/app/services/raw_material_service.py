from app.common.exceptions import (
    CategoryNotFoundError,
    RawMaterialNotFoundError,
    UnitNotFoundError,
)
from app.crud.category import get_category_by_id
from app.crud.raw_material import (
    create_raw_material,
    deactivate_raw_material,
    get_raw_material_by_code,
    get_raw_material_references,
    get_raw_materials,
    get_raw_materials_at_or_below_minimum_stock,
    update_raw_material,
)
from app.crud.unit import get_unit_by_id
from app.schemas.inventory_alert import RawMaterialLowStockResponse
from app.schemas.raw_material import RawMaterialCreate, RawMaterialUpdate
from app.schemas.raw_material_reference import (
    RawMaterialReferenceResponse,
)
from app.services.code_service import generate_code
from sqlalchemy.orm import Session


class RawMaterialService:
    @staticmethod
    def get_all(db: Session):

        return get_raw_materials(db)

    @staticmethod
    def create(db: Session, raw_material_data: RawMaterialCreate):

        category = get_category_by_id(db, raw_material_data.category_id)
        if not category:
            raise CategoryNotFoundError("The selected category does not exist.")

        unit = get_unit_by_id(db, raw_material_data.unit_id)
        if not unit:
            raise UnitNotFoundError("The selected unit does not exist.")

        return create_raw_material(
            db,
            raw_material_data,
            generate_code(db, "raw_material"),
        )

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

    @staticmethod
    def get_low_stock_alerts(
        db: Session,
    ) -> list[RawMaterialLowStockResponse]:
        rows = get_raw_materials_at_or_below_minimum_stock(db)

        return [
            RawMaterialLowStockResponse(
                raw_material_id=raw_material.id,
                raw_material_code=raw_material.code,
                raw_material_name=raw_material.name,
                unit_symbol=unit.symbol,
                current_stock=raw_material.current_stock,
                minimum_stock=raw_material.minimum_stock,
                shortage_quantity=(
                    raw_material.minimum_stock - raw_material.current_stock
                ),
            )
            for raw_material, unit in rows
        ]


    @staticmethod
    def get_references(
        db: Session,
    ) -> list[RawMaterialReferenceResponse]:
        rows = get_raw_material_references(db)

        return [
            RawMaterialReferenceResponse(
                id=raw_material.id,
                code=raw_material.code,
                name=raw_material.name,
                category_id=raw_material.category_id,
                unit_symbol=unit.symbol,
            )
            for raw_material, unit in rows
        ]
