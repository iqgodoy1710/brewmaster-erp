"""add keg movement operator audit

Revision ID: dc8a03bc378d
Revises: b81c3dd7cb3b
Create Date: 2026-08-26 07:12:53.211885
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "dc8a03bc378d"
down_revision: Union[str, Sequence[str], None] = "b81c3dd7cb3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "keg_movements",
        sa.Column(
            "performed_by_user_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_keg_movements_performed_by_user_id",
        "keg_movements",
        "users",
        ["performed_by_user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_keg_movements_performed_by_user_id",
        "keg_movements",
        type_="foreignkey",
    )
    op.drop_column(
        "keg_movements",
        "performed_by_user_id",
    )