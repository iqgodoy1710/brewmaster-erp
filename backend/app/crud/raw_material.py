from decimal import Decimal

from app.models.raw_material import RawMaterial
from app.models.unit import Unit
from app.schemas.raw_material import RawMaterialCreate, RawMaterialUpdate
from sqlalchemy.orm import Session


def get_raw_materials(db: Session):
    return (
        db.query(RawMaterial)
        .filter(RawMaterial.active.is_(True))
        .all()
    )

def create_raw_material(
    db: Session,
    raw_material_data: RawMaterialCreate,
    code: str,
):
    db_raw_material = RawMaterial(
        code=code,
        **raw_material_data.model_dump(),
    )

    db.add(db_raw_material)
    db.commit()
    db.refresh(db_raw_material)

    return db_raw_material

def get_raw_material_by_code(db: Session, code: str):
    return (
        db.query(RawMaterial)
        .filter(RawMaterial.code == code)
        .first()
    )

def update_raw_material(
        db: Session,
        raw_material: RawMaterial,
        raw_material_data: RawMaterialUpdate,
) -> RawMaterial:
    update_data = raw_material_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(raw_material, field, value)

    db.commit()
    db.refresh(raw_material)

    return raw_material

def update_raw_material_cost(
    db: Session,
    raw_material: RawMaterial,
    current_cost: Decimal,
) -> RawMaterial:
    raw_material.current_cost = current_cost

    db.flush()

    return raw_material

def deactivate_raw_material(
    db: Session,
    raw_material: RawMaterial,
) -> RawMaterial:
    raw_material.active = False

    db.commit()
    db.refresh(raw_material)

    return raw_material

def get_raw_material_by_id(
    db: Session,
    raw_material_id: int,
) -> RawMaterial | None:
    return (
        db.query(RawMaterial)
        .filter(RawMaterial.id == raw_material_id)
        .first()
    )


def update_raw_material_stock(
    db: Session,
    raw_material: RawMaterial,
    current_stock: Decimal,
) -> RawMaterial:
    raw_material.current_stock = current_stock

    db.flush()

    return raw_material

def get_raw_materials_at_or_below_minimum_stock(
    db: Session,
):
    return (
        db.query(RawMaterial, Unit)
        .join(
            Unit,
            RawMaterial.unit_id == Unit.id,
        )
        .filter(
            RawMaterial.active.is_(True),
            RawMaterial.minimum_stock > 0,
            RawMaterial.current_stock <= RawMaterial.minimum_stock,
        )
        .order_by(RawMaterial.name)
        .all()
    )

def get_raw_material_references(
    db: Session,
):
    return (
        db.query(RawMaterial, Unit)
        .join(
            Unit,
            RawMaterial.unit_id == Unit.id,
        )
        .filter(RawMaterial.active.is_(True))
        .order_by(RawMaterial.name)
        .all()
    )