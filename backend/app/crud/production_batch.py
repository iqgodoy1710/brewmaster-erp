from app.models.enums import ProductionBatchStatus
from app.models.production_batch import ProductionBatch
from app.models.raw_material import RawMaterial
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.unit import Unit
from app.schemas.production_batch import ProductionBatchCreate
from sqlalchemy.orm import Session


def get_production_batches(
    db: Session,
) -> list[ProductionBatch]:
    return (
        db.query(ProductionBatch)
        .filter(ProductionBatch.active.is_(True))
        .all()
    )


def get_production_batch_by_code(
    db: Session,
    code: str,
) -> ProductionBatch | None:
    return (
        db.query(ProductionBatch)
        .filter(ProductionBatch.code == code)
        .first()
    )


def create_production_batch(
    db: Session,
    production_batch_data: ProductionBatchCreate,
) -> ProductionBatch:
    production_batch = ProductionBatch(
        **production_batch_data.model_dump()
    )

    db.add(production_batch)
    db.commit()
    db.refresh(production_batch)

    return production_batch

def get_planned_production_batch_requirements(
    db: Session,
):
    return (
        db.query(
            ProductionBatch,
            Recipe,
            RecipeIngredient,
            RawMaterial,
            Unit,
        )
        .join(
            Recipe,
            ProductionBatch.recipe_id == Recipe.id,
        )
        .join(
            RecipeIngredient,
            RecipeIngredient.recipe_id == Recipe.id,
        )
        .join(
            RawMaterial,
            RecipeIngredient.raw_material_id == RawMaterial.id,
        )
        .join(
            Unit,
            RawMaterial.unit_id == Unit.id,
        )
        .filter(
            ProductionBatch.active.is_(True),
            ProductionBatch.status == ProductionBatchStatus.PLANNED,
        )
        .all()
    )