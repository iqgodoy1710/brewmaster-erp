"""create raw material cost history

Revision ID: 789cc1e040ee
Revises: 54e41c796af6
Create Date: 2026-09-22 20:47:09.199851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '789cc1e040ee'
down_revision: Union[str, Sequence[str], None] = '54e41c796af6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
cost_change_source = postgresql.ENUM(
    "purchase_receipt",
    "manual_update",
    name="raw_material_cost_change_source",
    create_type=False,
)

def upgrade() -> None:
    cost_change_source.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "raw_material_cost_history",
        sa.Column("raw_material_id", sa.Integer(), nullable=False),
        sa.Column("stock_movement_id", sa.Integer(), nullable=True),
        sa.Column("source", cost_change_source, nullable=False),
        sa.Column(
            "previous_cost",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "new_cost",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "occurred_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "new_cost >= 0",
            name="ck_raw_material_cost_history_new_cost_non_negative",
        ),
        sa.CheckConstraint(
            "previous_cost >= 0",
            name="ck_raw_material_cost_history_previous_cost_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["raw_material_id"],
            ["raw_materials.id"],
        ),
        sa.ForeignKeyConstraint(
            ["stock_movement_id"],
            ["raw_material_stock_movements.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_movement_id"),
    )

def downgrade() -> None:
    op.drop_table("raw_material_cost_history")

    cost_change_source.drop(
        op.get_bind(),
        checkfirst=True,
    )