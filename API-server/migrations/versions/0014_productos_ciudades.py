"""crea tabla de relacion productos_ciudades (UNIQUE par)

Revision ID: 0014_productos_ciudades
Revises: 0013_productos_vehiculos
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0014_productos_ciudades"
down_revision = "0013_productos_vehiculos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "productos_ciudades",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("ciudad_id", sa.Integer(), sa.ForeignKey("ciudades.id"), nullable=False),
        sa.UniqueConstraint("producto_id", "ciudad_id", name="uq_productos_ciudades"),
    )


def downgrade() -> None:
    op.drop_table("productos_ciudades")
