from decimal import Decimal

from app.models.enums import ProductionBatchStatus
from app.models.production_batch import ProductionBatch
from app.models.raw_material import RawMaterial
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.unit import Unit
from app.schemas.production_batch import ProductionBatchCreate
from sqlalchemy.orm import Session
from sqlalchemy.sql import func


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

def complete_production_batch(
    db: Session,
    production_batch: ProductionBatch,
    produced_volume_liters: Decimal,
) -> ProductionBatch:
    production_batch.produced_volume_liters = produced_volume_liters
    production_batch.available_bulk_volume_liters = produced_volume_liters
    production_batch.status = ProductionBatchStatus.COMPLETED
    production_batch.completed_at = func.now()

    db.flush()

    return production_batch

def get_production_batch_by_id(
    db: Session,
    production_batch_id: int,
) -> ProductionBatch | None:
    return (
        db.query(ProductionBatch)
        .filter(ProductionBatch.id == production_batch_id)
        .first()
    )


def update_available_bulk_volume(
    db: Session,
    production_batch: ProductionBatch,
    available_bulk_volume_liters: Decimal,
) -> ProductionBatch:
    production_batch.available_bulk_volume_liters = (
        available_bulk_volume_liters
    )

    db.flush()

    return production_batch