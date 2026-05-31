"""crea tabla de relacion leads_productos (productos de interes; UNIQUE par)

Revision ID: 0016_leads_productos
Revises: 0015_productos_categorias
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0016_leads_productos"
down_revision = "0015_productos_categorias"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leads_productos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("productos.id"), nullable=False),
        sa.UniqueConstraint("lead_id", "producto_id", name="uq_leads_productos"),
    )


def downgrade() -> None:
    op.drop_table("leads_productos")
