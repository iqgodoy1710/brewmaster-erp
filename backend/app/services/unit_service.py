from app.common.exceptions import (
    UnitNameAlreadyExistsError,
    UnitSymbolAlreadyExistsError,
)
from app.crud.unit import (
    create_unit,
    get_unit_by_name,
    get_unit_by_symbol,
    get_units,
)
from app.schemas.unit import UnitCreate
from sqlalchemy.orm import Session


class UnitService:
    @staticmethod
    def get_all(db: Session):
        return get_units(db)

    @staticmethod
    def create(
        db: Session,
        unit_data: UnitCreate,
    ):
        existing_name = get_unit_by_name(db, unit_data.name)
        if existing_name:
            raise UnitNameAlreadyExistsError(
                "A unit with this name already exists."
            )

        existing_symbol = get_unit_by_symbol(db, unit_data.symbol)
        if existing_symbol:
            raise UnitSymbolAlreadyExistsError(
                "A unit with this symbol already exists."
            )

        return create_unit(db, unit_data)