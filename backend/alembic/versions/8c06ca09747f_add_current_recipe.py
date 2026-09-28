"""add current recipe

Revision ID: 8c06ca09747f
Revises: 14ec7226cb98
Create Date: 2026-09-28 21:42:29.575414
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c06ca09747f"
down_revision: Union[str, Sequence[str], None] = "14ec7226cb98"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column(
            "is_current",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )

    op.execute(
        """
        UPDATE recipes
        SET is_current = true
        WHERE id IN (
            SELECT DISTINCT ON (beer_id) id
            FROM recipes
            WHERE active = true
            ORDER BY beer_id, version DESC, id DESC
        )
        """
    )

    op.create_index(
        "uq_recipes_current_per_beer",
        "recipes",
        ["beer_id"],
        unique=True,
        postgresql_where=sa.text("is_current = true"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_recipes_current_per_beer",
        table_name="recipes",
    )

    op.drop_column(
        "recipes",
        "is_current",
    )