from sqlalchemy.orm import Session
from app.schemas.raw_material import RawMaterialCreate, RawMaterialUpdate
from app.models.raw_material import RawMaterial



def get_raw_materials(db: Session):
    return (
        db.query(RawMaterial)
        .filter(RawMaterial.active.is_(True))
        .all()
    )

def create_raw_material(db: Session, raw_material_data: RawMaterialCreate):
    db_raw_material = RawMaterial(**raw_material_data.model_dump())
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

def deactivate_raw_material(
    db: Session,
    raw_material: RawMaterial,
) -> RawMaterial:
    raw_material.active = False

    db.commit()
    db.refresh(raw_material)

    return raw_material