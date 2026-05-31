"""crea tabla monedas (catalogo Tier 1)

Revision ID: 0001_monedas
Revises:
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_monedas"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "monedas",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("moneda", sa.String(255), nullable=False),
        sa.Column("abreviacion", sa.String(10), nullable=False),
        sa.Column("tipo_de_cambio", sa.Integer(), nullable=False),
        sa.UniqueConstraint("abreviacion", name="uq_monedas_abreviacion"),
    )


def downgrade() -> None:
    op.drop_table("monedas")
