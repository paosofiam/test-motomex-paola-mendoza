"""crea tabla intenciones_de_compra_de_leads (catalogo Tier 1)

Revision ID: 0003_intenciones
Revises: 0002_estados
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_intenciones"
down_revision = "0002_estados"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intenciones_de_compra_de_leads",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("tipo", sa.String(50), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("intenciones_de_compra_de_leads")
