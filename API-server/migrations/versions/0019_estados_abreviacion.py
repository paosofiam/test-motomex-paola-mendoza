"""agrega columna abreviacion a estados (resolucion por nombre o abreviacion)

Revision ID: 0019_estados_abreviacion
Revises: 0018_pre_ordenes_productos
Create Date: 2026-06-05
"""

from alembic import op
import sqlalchemy as sa

revision = "0019_estados_abreviacion"
down_revision = "0018_pre_ordenes_productos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("estados", sa.Column("abreviacion", sa.String(10), nullable=True))


def downgrade() -> None:
    op.drop_column("estados", "abreviacion")
