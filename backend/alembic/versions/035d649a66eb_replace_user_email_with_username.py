"""replace user email with username

Revision ID: 035d649a66eb
Revises: eaffbaf5896d
Create Date: 2026-08-19 10:38:07.473494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '035d649a66eb'
down_revision: Union[str, Sequence[str], None] = 'eaffbaf5896d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "email",
        new_column_name="username",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "username",
        new_column_name="email",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=False,
    )