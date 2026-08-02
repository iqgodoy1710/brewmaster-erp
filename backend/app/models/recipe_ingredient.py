from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.common.base_model import BaseModel


class RecipeIngredient(BaseModel):
    __tablename__ = "recipe_ingredients"

    __table_args__ = (
        CheckConstraint(
            "required_quantity > 0",
            name="ck_recipe_ingredients_required_quantity_positive",
        ),
        UniqueConstraint(
            "recipe_id",
            "raw_material_id",
            name="uq_recipe_ingredients_recipe_id_raw_material_id",
        ),
    )

    recipe_id = Column(
        Integer,
        ForeignKey("recipes.id"),
        nullable=False,
    )
    raw_material_id = Column(
        Integer,
        ForeignKey("raw_materials.id"),
        nullable=False,
    )
    required_quantity = Column(
        Numeric(10, 3),
        nullable=False,
    )

    recipe = relationship(
        "Recipe",
        back_populates="ingredients",
    )
    raw_material = relationship(
        "RawMaterial",
        back_populates="recipe_ingredients",
    )