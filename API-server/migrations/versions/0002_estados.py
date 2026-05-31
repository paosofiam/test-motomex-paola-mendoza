"""crea tabla estados (catalogo Tier 1)

Revision ID: 0002_estados
Revises: 0001_monedas
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_estados"
down_revision = "0001_monedas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "estados",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("estado", sa.String(255), nullable=False),
        sa.UniqueConstraint("estado", name="uq_estados_estado"),
    )


def downgrade() -> None:
    op.drop_table("estados")
