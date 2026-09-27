"""add keg repackaging reversal

Revision ID: 99001bf9e67a
Revises: 23ba9dacfc52
Create Date: 2026-09-27 13:47:37.021778
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "99001bf9e67a"
down_revision: Union[str, Sequence[str], None] = "23ba9dacfc52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE beer_presentation_stock_movement_type "
        "ADD VALUE IF NOT EXISTS 'repackaging_reversal_in'"
    )

    op.execute(
        "ALTER TYPE beer_presentation_stock_movement_type "
        "ADD VALUE IF NOT EXISTS 'repackaging_reversal_out'"
    )

    op.execute(
        "ALTER TYPE raw_material_movement_type "
        "ADD VALUE IF NOT EXISTS 'repackaging_reversal'"
    )

    op.execute(
        "ALTER TYPE keg_movement_type "
        "ADD VALUE IF NOT EXISTS 'repackaging_reversal'"
    )

    op.add_column(
        "keg_repackaging_runs",
        sa.Column(
            "reversed_at",
            sa.TIMESTAMP(),
            nullable=True,
        ),
    )

    op.add_column(
        "keg_repackaging_runs",
        sa.Column(
            "reversed_by_user_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "keg_repackaging_runs",
        sa.Column(
            "reversal_reason",
            sa.Text(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_keg_repackaging_runs_reversed_by_user_id",
        "keg_repackaging_runs",
        "users",
        ["reversed_by_user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_keg_repackaging_runs_reversed_by_user_id",
        "keg_repackaging_runs",
        type_="foreignkey",
    )

    op.drop_column(
        "keg_repackaging_runs",
        "reversal_reason",
    )

    op.drop_column(
        "keg_repackaging_runs",
        "reversed_by_user_id",
    )

    op.drop_column(
        "keg_repackaging_runs",
        "reversed_at",
    )