"""create keg repackaging runs

Revision ID: 9adbacbb9944
Revises: dc8a03bc378d
Create Date: 2026-08-30 12:16:28.158864

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9adbacbb9944"
down_revision: Union[str, Sequence[str], None] = "dc8a03bc378d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "keg_repackaging_runs",
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("keg_id", sa.Integer(), nullable=False),
        sa.Column(
            "source_beer_presentation_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "target_beer_presentation_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "production_batch_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column("packaged_quantity", sa.Integer(), nullable=False),
        sa.Column(
            "packaged_volume_liters",
            sa.Numeric(precision=10, scale=3),
            nullable=False,
        ),
        sa.Column(
            "remaining_volume_liters",
            sa.Numeric(precision=10, scale=3),
            nullable=False,
        ),
        sa.Column(
            "waste_volume_liters",
            sa.Numeric(precision=10, scale=3),
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
        sa.Column("notes", sa.Text(), nullable=True),
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
            "packaged_quantity > 0",
            name=("ck_keg_repackaging_runs_packaged_quantity_positive"),
        ),
        sa.CheckConstraint(
            "packaged_volume_liters > 0",
            name=("ck_keg_repackaging_runs_packaged_volume_positive"),
        ),
        sa.CheckConstraint(
            "remaining_volume_liters >= 0",
            name=("ck_keg_repackaging_runs_remaining_volume_non_negative"),
        ),
        sa.CheckConstraint(
            "waste_volume_liters >= 0",
            name=("ck_keg_repackaging_runs_waste_volume_non_negative"),
        ),
        sa.ForeignKeyConstraint(["keg_id"], ["kegs.id"]),
        sa.ForeignKeyConstraint(
            ["source_beer_presentation_id"],
            ["beer_presentations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["target_beer_presentation_id"],
            ["beer_presentations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["production_batch_id"],
            ["production_batches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["performed_by_user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.execute(
        "ALTER TYPE beer_presentation_stock_movement_type "
        "ADD VALUE IF NOT EXISTS 'repackaging_consumption'"
    )
    op.execute(
        "ALTER TYPE beer_presentation_stock_movement_type "
        "ADD VALUE IF NOT EXISTS 'repackaging_receipt'"
    )
    op.execute("ALTER TYPE keg_movement_type ADD VALUE IF NOT EXISTS 'repackaging'")

    op.add_column(
        "beer_presentation_stock_movements",
        sa.Column(
            "keg_repackaging_run_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_bpsm_keg_repackaging_run_id",
        "beer_presentation_stock_movements",
        "keg_repackaging_runs",
        ["keg_repackaging_run_id"],
        ["id"],
    )

    op.add_column(
        "raw_material_stock_movements",
        sa.Column(
            "keg_repackaging_run_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_rmsm_keg_repackaging_run_id",
        "raw_material_stock_movements",
        "keg_repackaging_runs",
        ["keg_repackaging_run_id"],
        ["id"],
    )

    op.add_column(
        "keg_movements",
        sa.Column(
            "keg_repackaging_run_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_keg_movements_keg_repackaging_run_id",
        "keg_movements",
        "keg_repackaging_runs",
        ["keg_repackaging_run_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_keg_movements_keg_repackaging_run_id",
        "keg_movements",
        type_="foreignkey",
    )
    op.drop_column(
        "keg_movements",
        "keg_repackaging_run_id",
    )

    op.drop_constraint(
        "fk_rmsm_keg_repackaging_run_id",
        "raw_material_stock_movements",
        type_="foreignkey",
    )
    op.drop_column(
        "raw_material_stock_movements",
        "keg_repackaging_run_id",
    )

    op.drop_constraint(
        "fk_bpsm_keg_repackaging_run_id",
        "beer_presentation_stock_movements",
        type_="foreignkey",
    )
    op.drop_column(
        "beer_presentation_stock_movements",
        "keg_repackaging_run_id",
    )
    op.drop_table("keg_repackaging_runs")
