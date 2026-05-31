"""crea tabla productos (Tier 3; FK marcas y monedas; precio/centavos; moneda_id default 1)

Revision ID: 0009_productos
Revises: 0008_vehiculos
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0009_productos"
down_revision = "0008_vehiculos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "productos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("marca_id", sa.Integer(), sa.ForeignKey("marcas.id"), nullable=False),
        sa.Column("modelo", sa.String(255), nullable=False),
        sa.Column("precio", sa.Integer(), nullable=False),  # centavos (moneda original)
        sa.Column("moneda_id", sa.Integer(), sa.ForeignKey("monedas.id"), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("especificaciones", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("productos")
