"""crea tabla vehiculos (catalogo Tier 2; FK marcas; UNIQUE compuesto modelo+marca_id+anio)

Revision ID: 0008_vehiculos
Revises: 0007_ciudades
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0008_vehiculos"
down_revision = "0007_ciudades"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehiculos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("modelo", sa.String(255), nullable=False),
        sa.Column("marca_id", sa.Integer(), sa.ForeignKey("marcas.id"), nullable=False),
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.UniqueConstraint("modelo", "marca_id", "anio", name="uq_vehiculos_modelo_marca_anio"),
    )


def downgrade() -> None:
    op.drop_table("vehiculos")
