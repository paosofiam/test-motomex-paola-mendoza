"""crea tabla de relacion pre_ordenes_productos (con cantidad; UNIQUE par)

Revision ID: 0018_pre_ordenes_productos
Revises: 0017_leads_vehiculos
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0018_pre_ordenes_productos"
down_revision = "0017_leads_vehiculos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pre_ordenes_productos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("pre_orden_id", sa.Integer(), sa.ForeignKey("pre_ordenes.id"), nullable=False),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.UniqueConstraint("pre_orden_id", "producto_id", name="uq_pre_ordenes_productos"),
    )


def downgrade() -> None:
    op.drop_table("pre_ordenes_productos")
