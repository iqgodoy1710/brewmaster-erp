"""normalize migrated usernames

Revision ID: eb9e703dd86c
Revises: 035d649a66eb
Create Date: 2026-08-19 12:02:31.645752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb9e703dd86c'
down_revision: Union[str, Sequence[str], None] = '035d649a66eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE users
        SET username = CONCAT(
            'legacy-',
            id::text,
            '-',
            LEFT(
                REGEXP_REPLACE(
                    LOWER(SPLIT_PART(username, '@', 1)),
                    '[^a-z0-9._-]',
                    '-',
                    'g'
                ),
                30
            )
        )
        WHERE username LIKE '%@%';
        """
    )


def downgrade() -> None:
    pass