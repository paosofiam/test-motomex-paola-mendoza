"""crea tabla marcas (catalogo Tier 2, valor normalizado UNIQUE)

Revision ID: 0005_marcas
Revises: 0004_chat_statuses
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_marcas"
down_revision = "0004_chat_statuses"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "marcas",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("marca", sa.String(255), nullable=False),
        sa.UniqueConstraint("marca", name="uq_marcas_marca"),
    )


def downgrade() -> None:
    op.drop_table("marcas")
