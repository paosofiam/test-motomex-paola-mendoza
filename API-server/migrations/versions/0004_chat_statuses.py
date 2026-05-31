"""crea tabla chat_statuses (catalogo Tier 1 estatico)

Revision ID: 0004_chat_statuses
Revises: 0003_intenciones
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_chat_statuses"
down_revision = "0003_intenciones"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_statuses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("chat_statuses")
