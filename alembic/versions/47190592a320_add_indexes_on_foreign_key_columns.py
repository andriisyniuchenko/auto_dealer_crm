"""add indexes on foreign key columns

Revision ID: 47190592a320
Revises: d5c3ae5df43e
Create Date: 2026-05-31 22:17:06.615227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47190592a320'
down_revision: Union[str, Sequence[str], None] = 'd5c3ae5df43e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f("ix_appointments_lead_id"), "appointments", ["lead_id"], unique=False)
    op.create_index(op.f("ix_appointments_user_id"), "appointments", ["user_id"], unique=False)
    op.create_index(op.f("ix_deals_lead_id"), "deals", ["lead_id"], unique=False)
    op.create_index(op.f("ix_activities_lead_id"), "activities", ["lead_id"], unique=False)
    op.create_index(op.f("ix_activities_user_id"), "activities", ["user_id"], unique=False)
    op.create_index(op.f("ix_notes_lead_id"), "notes", ["lead_id"], unique=False)
    op.create_index(op.f("ix_notes_user_id"), "notes", ["user_id"], unique=False)
    op.create_index(op.f("ix_chat_sessions_lead_id"), "chat_sessions", ["lead_id"], unique=False)
    op.create_index(op.f("ix_chat_messages_session_id"), "chat_messages", ["session_id"], unique=False)
    op.create_index(op.f("ix_lead_salespeople_user_id"), "lead_salespeople", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_lead_salespeople_user_id"), table_name="lead_salespeople")
    op.drop_index(op.f("ix_chat_messages_session_id"), table_name="chat_messages")
    op.drop_index(op.f("ix_chat_sessions_lead_id"), table_name="chat_sessions")
    op.drop_index(op.f("ix_notes_user_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_lead_id"), table_name="notes")
    op.drop_index(op.f("ix_activities_user_id"), table_name="activities")
    op.drop_index(op.f("ix_activities_lead_id"), table_name="activities")
    op.drop_index(op.f("ix_deals_lead_id"), table_name="deals")
    op.drop_index(op.f("ix_appointments_user_id"), table_name="appointments")
    op.drop_index(op.f("ix_appointments_lead_id"), table_name="appointments")
