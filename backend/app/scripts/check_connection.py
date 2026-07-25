from app.db.database import SessionLocal

from app.schemas.raw_material import RawMaterialCreate
from app.crud.raw_material import create_raw_material

db = SessionLocal()

data = RawMaterialCreate(
    code="MALT-002",
    name="Munich",
    category_id=1,
    unit_id=1,
    current_stock=100,
    minimum_stock=20,
    current_cost=2400,
    description="Malta Munich"
    )
new_raw_material = create_raw_material(db, data)




db.close()