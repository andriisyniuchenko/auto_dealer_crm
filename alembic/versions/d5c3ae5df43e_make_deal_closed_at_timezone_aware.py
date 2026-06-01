"""make deal closed_at timezone aware

Revision ID: d5c3ae5df43e
Revises: 0fd49a77bd4b
Create Date: 2026-05-31 22:06:00.994001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5c3ae5df43e'
down_revision: Union[str, Sequence[str], None] = '0fd49a77bd4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "deals",
        "closed_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="closed_at AT TIME ZONE 'UTC'",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "deals",
        "closed_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="closed_at AT TIME ZONE 'UTC'",
    )
