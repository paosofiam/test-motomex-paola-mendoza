"""crea tabla ciudades (catalogo Tier 2; FK estados; valor normalizado UNIQUE)

Revision ID: 0007_ciudades
Revises: 0006_categorias
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_ciudades"
down_revision = "0006_categorias"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ciudades",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("ciudad", sa.String(255), nullable=False),
        sa.Column("estado_id", sa.Integer(), sa.ForeignKey("estados.id"), nullable=False),
        sa.UniqueConstraint("ciudad", name="uq_ciudades_ciudad"),
    )


def downgrade() -> None:
    op.drop_table("ciudades")
