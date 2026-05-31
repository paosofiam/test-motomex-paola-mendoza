"""crea tabla chats (Tier 3; FK leads y chat_statuses; indices whatsapp y (lead_id,created_at))

Revision ID: 0011_chats
Revises: 0010_leads
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0011_chats"
down_revision = "0010_leads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chats",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("chat_whatsapp_id", sa.String(255), nullable=False),
        sa.Column("chat_status_id", sa.Integer(), sa.ForeignKey("chat_statuses.id"), nullable=False),
        sa.Column("resumen", sa.Text(), nullable=True),
    )
    op.create_index("ix_chats_chat_whatsapp_id", "chats", ["chat_whatsapp_id"])
    op.create_index("ix_chats_lead_id_created_at", "chats", ["lead_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_chats_lead_id_created_at", table_name="chats")
    op.drop_index("ix_chats_chat_whatsapp_id", table_name="chats")
    op.drop_table("chats")
