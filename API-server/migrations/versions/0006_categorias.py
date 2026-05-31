"""crea tabla categorias (catalogo Tier 2, valor normalizado UNIQUE)

Revision ID: 0006_categorias
Revises: 0005_marcas
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_categorias"
down_revision = "0005_marcas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("categoria", sa.String(255), nullable=False),
        sa.UniqueConstraint("categoria", name="uq_categorias_categoria"),
    )


def downgrade() -> None:
    op.drop_table("categorias")
