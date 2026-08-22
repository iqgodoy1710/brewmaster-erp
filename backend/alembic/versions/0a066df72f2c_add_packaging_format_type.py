"""add packaging format type

Revision ID: 0a066df72f2c
Revises: cff961940f7e
Create Date: 2026-08-20 15:24:25.811867

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0a066df72f2c"
down_revision: Union[str, Sequence[str], None] = "cff961940f7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
packaging_format_type = sa.Enum(
    "bottle",
    "keg",
    "can",
    "other",
    name="packaging_format_type",
)


def upgrade() -> None:
    packaging_format_type.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.add_column(
        "packaging_formats",
        sa.Column(
            "format_type",
            packaging_format_type,
            server_default="other",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "packaging_formats",
        "format_type",
    )

    packaging_format_type.drop(
        op.get_bind(),
        checkfirst=True,
    )