"""crea tabla leads (Tier 3; FK ciudades nullable e intenciones; indice chat_whatsapp_id)

Revision ID: 0010_leads
Revises: 0009_productos
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0010_leads"
down_revision = "0009_productos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("chat_whatsapp_id", sa.String(255), nullable=False),
        sa.Column("nombre_whatsapp", sa.String(255), nullable=False),
        sa.Column("telefono", sa.String(15), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=True),
        sa.Column("ciudad_id", sa.Integer(), sa.ForeignKey("ciudades.id"), nullable=True),
        sa.Column("direccion_envio", sa.String(512), nullable=True),
        sa.Column(
            "intencion_de_compra_id",
            sa.Integer(),
            sa.ForeignKey("intenciones_de_compra_de_leads.id"),
            nullable=False,
        ),
    )
    op.create_index("ix_leads_chat_whatsapp_id", "leads", ["chat_whatsapp_id"])


def downgrade() -> None:
    op.drop_index("ix_leads_chat_whatsapp_id", table_name="leads")
    op.drop_table("leads")
