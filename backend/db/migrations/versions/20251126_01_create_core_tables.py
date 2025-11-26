"""Create core auth/chat tables

Revision ID: 20251126_01
Revises: 
Create Date: 2025-11-26 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251126_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    op.create_table(
        "chatsession",
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chatsession_title", "chatsession", ["title"], unique=False)
    op.create_index("ix_chatsession_user_id", "chatsession", ["user_id"], unique=False)

    op.create_table(
        "chatmessage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["chatsession.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chatmessage_session_id", "chatmessage", ["session_id"], unique=False)
    op.create_index("ix_chatmessage_role", "chatmessage", ["role"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_chatmessage_role", table_name="chatmessage")
    op.drop_index("ix_chatmessage_session_id", table_name="chatmessage")
    op.drop_table("chatmessage")

    op.drop_index("ix_chatsession_user_id", table_name="chatsession")
    op.drop_index("ix_chatsession_title", table_name="chatsession")
    op.drop_table("chatsession")

    op.drop_index("ix_user_email", table_name="user")
    op.drop_table("user")
