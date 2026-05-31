"""crea tabla de relacion productos_categorias (UNIQUE par)

Revision ID: 0015_productos_categorias
Revises: 0014_productos_ciudades
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0015_productos_categorias"
down_revision = "0014_productos_ciudades"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "productos_categorias",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("categoria_id", sa.Integer(), sa.ForeignKey("categorias.id"), nullable=False),
        sa.UniqueConstraint("producto_id", "categoria_id", name="uq_productos_categorias"),
    )


def downgrade() -> None:
    op.drop_table("productos_categorias")
