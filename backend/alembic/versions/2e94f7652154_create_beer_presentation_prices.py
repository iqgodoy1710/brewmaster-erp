"""create beer presentation prices

Revision ID: 2e94f7652154
Revises: 2a144f0e76d5
Create Date: 2026-08-19 15:45:44.530617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e94f7652154'
down_revision: Union[str, Sequence[str], None] = '2a144f0e76d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "beer_presentation_prices",
        sa.Column(
            "beer_presentation_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "unit_price",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "effective_from",
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
            "unit_price > 0",
            name=(
                "ck_beer_presentation_prices_"
                "unit_price_positive"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["beer_presentation_id"],
            ["beer_presentations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_beer_presentation_prices_active_presentation",
        "beer_presentation_prices",
        ["beer_presentation_id"],
        unique=True,
        postgresql_where=sa.text("active = true"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_beer_presentation_prices_active_presentation",
        table_name="beer_presentation_prices",
    )
    op.drop_table("beer_presentation_prices")