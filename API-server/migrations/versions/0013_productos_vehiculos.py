"""crea tabla de relacion productos_vehiculos (UNIQUE par)

Revision ID: 0013_productos_vehiculos
Revises: 0012_pre_ordenes
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0013_productos_vehiculos"
down_revision = "0012_pre_ordenes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "productos_vehiculos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("vehiculo_id", sa.Integer(), sa.ForeignKey("vehiculos.id"), nullable=False),
        sa.UniqueConstraint("producto_id", "vehiculo_id", name="uq_productos_vehiculos"),
    )


def downgrade() -> None:
    op.drop_table("productos_vehiculos")
