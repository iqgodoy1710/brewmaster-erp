"""create bottle pasteurization runs

Revision ID: 23ba9dacfc52
Revises: 789cc1e040ee
Create Date: 2026-09-27 11:20:23.537911
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "23ba9dacfc52"
down_revision: Union[str, Sequence[str], None] = "789cc1e040ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE beer_presentation_stock_movement_type "
        "ADD VALUE IF NOT EXISTS 'pasteurization_waste'"
    )

    op.create_table(
        "bottle_pasteurization_runs",
        sa.Column(
            "code",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "beer_presentation_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "processed_quantity",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "approved_quantity",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "waste_quantity",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "performed_by_user_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "occurred_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
        ),
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
            "processed_quantity > 0",
            name=(
                "ck_bottle_pasteurization_runs_"
                "processed_quantity_positive"
            ),
        ),
        sa.CheckConstraint(
            "approved_quantity >= 0",
            name=(
                "ck_bottle_pasteurization_runs_"
                "approved_quantity_non_negative"
            ),
        ),
        sa.CheckConstraint(
            "waste_quantity >= 0",
            name=(
                "ck_bottle_pasteurization_runs_"
                "waste_quantity_non_negative"
            ),
        ),
        sa.CheckConstraint(
            "processed_quantity = approved_quantity + waste_quantity",
            name=(
                "ck_bottle_pasteurization_runs_"
                "quantity_balance"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["beer_presentation_id"],
            ["beer_presentations.id"],
            name=(
                "fk_bottle_pasteurization_runs_"
                "beer_presentation_id"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["performed_by_user_id"],
            ["users.id"],
            name=(
                "fk_bottle_pasteurization_runs_"
                "performed_by_user_id"
            ),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.add_column(
        "beer_presentation_stock_movements",
        sa.Column(
            "pasteurization_run_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_bpsm_pasteurization_run_id",
        "beer_presentation_stock_movements",
        "bottle_pasteurization_runs",
        ["pasteurization_run_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_bpsm_pasteurization_run_id",
        "beer_presentation_stock_movements",
        type_="foreignkey",
    )

    op.drop_column(
        "beer_presentation_stock_movements",
        "pasteurization_run_id",
    )

    op.drop_table("bottle_pasteurization_runs")