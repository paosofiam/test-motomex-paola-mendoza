"""crea tabla pre_ordenes (Tier 3; FK leads; total en MXN/centavos; sin moneda_id)

Revision ID: 0012_pre_ordenes
Revises: 0011_chats
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0012_pre_ordenes"
down_revision = "0011_chats"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pre_ordenes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),  # centavos, MXN ya convertido
    )


def downgrade() -> None:
    op.drop_table("pre_ordenes")
