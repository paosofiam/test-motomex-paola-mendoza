"""crea tabla de relacion leads_vehiculos (vehiculos del lead; UNIQUE par)

Revision ID: 0017_leads_vehiculos
Revises: 0016_leads_productos
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0017_leads_vehiculos"
down_revision = "0016_leads_productos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leads_vehiculos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("vehiculo_id", sa.Integer(), sa.ForeignKey("vehiculos.id"), nullable=False),
        sa.UniqueConstraint("lead_id", "vehiculo_id", name="uq_leads_vehiculos"),
    )


def downgrade() -> None:
    op.drop_table("leads_vehiculos")
