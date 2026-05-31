"""add appointment notes

Revision ID: 0fd49a77bd4b
Revises: 3d58c85aa4ba
Create Date: 2026-05-31 13:20:20.193189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fd49a77bd4b'
down_revision: Union[str, Sequence[str], None] = '3d58c85aa4ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("appointments", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("appointments", "notes")
