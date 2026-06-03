"""Tabla de relación N:M leads_productos (productos de interés). Sin métodos propios: las filas se gestionan desde LeadModel.

Columnas estándar + 2 FKs + UNIQUE(lead_id, producto_id). La relación `producto`
(solo mapeo) permite que LeadModel exponga `productos_interes` como [modelo].
"""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampMixin
from app.database import Base


class LeadProductoModel(TimestampMixin, Base):
    __tablename__ = "leads_productos"
    __table_args__ = (
        UniqueConstraint("lead_id", "producto_id", name="uq_leads_productos"),
    )

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)

    producto: Mapped["ProductoModel"] = relationship(lazy="joined")  # noqa: F821
