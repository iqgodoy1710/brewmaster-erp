"""add keg transfer movement types

Revision ID: 54e41c796af6
Revises: 6ed85a92d073
Create Date: 2026-09-05 10:56:03.003409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54e41c796af6'
down_revision: Union[str, Sequence[str], None] = '6ed85a92d073'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE keg_movement_type "
        "ADD VALUE IF NOT EXISTS 'transfer'"
    )
    op.execute(
        "ALTER TYPE beer_presentation_stock_movement_type "
        "ADD VALUE IF NOT EXISTS 'keg_transfer_consumption'"
    )
    op.execute(
        "ALTER TYPE beer_presentation_stock_movement_type "
        "ADD VALUE IF NOT EXISTS 'keg_transfer_receipt'"
    )


def downgrade() -> None:
    # PostgreSQL no permite quitar valores de un ENUM de forma segura.
    pass

