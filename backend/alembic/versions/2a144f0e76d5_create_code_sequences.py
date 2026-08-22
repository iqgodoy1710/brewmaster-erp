"""create code sequences

Revision ID: 2a144f0e76d5
Revises: eb9e703dd86c
Create Date: 2026-08-19 14:55:19.726464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a144f0e76d5'
down_revision: Union[str, Sequence[str], None] = 'eb9e703dd86c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "code_sequences",
        sa.Column(
            "entity_key",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "last_value",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.CheckConstraint(
            "last_value >= 0",
            name="ck_code_sequences_last_value_non_negative",
        ),
        sa.PrimaryKeyConstraint("entity_key"),
    )


def downgrade() -> None:
    op.drop_table("code_sequences")
