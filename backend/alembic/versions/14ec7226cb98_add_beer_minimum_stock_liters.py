"""add beer minimum stock liters

Revision ID: 14ec7226cb98
Revises: 99001bf9e67a
Create Date: 2026-09-27 21:02:20.843541
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "14ec7226cb98"
down_revision: Union[str, Sequence[str], None] = "99001bf9e67a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "beers",
        sa.Column(
            "minimum_stock_liters",
            sa.Numeric(precision=10, scale=3),
            server_default="0",
            nullable=False,
        ),
    )

    op.create_check_constraint(
        "ck_beers_minimum_stock_liters_non_negative",
        "beers",
        "minimum_stock_liters >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_beers_minimum_stock_liters_non_negative",
        "beers",
        type_="check",
    )

    op.drop_column(
        "beers",
        "minimum_stock_liters",
    )