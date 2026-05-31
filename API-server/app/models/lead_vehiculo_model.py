"""Tabla de relación N:M leads_vehiculos (vehículos del lead). Sin métodos (pendiente).

Columnas estándar + 2 FKs + UNIQUE(lead_id, vehiculo_id). La relación `vehiculo`
(solo mapeo) permite que LeadModel exponga `vehiculo` como [{modelo, marca, anio}].
"""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampMixin
from app.database import Base


class LeadVehiculoModel(TimestampMixin, Base):
    __tablename__ = "leads_vehiculos"
    __table_args__ = (
        UniqueConstraint("lead_id", "vehiculo_id", name="uq_leads_vehiculos"),
    )

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    vehiculo_id: Mapped[int] = mapped_column(ForeignKey("vehiculos.id"), nullable=False)

    vehiculo: Mapped["VehiculoModel"] = relationship(lazy="joined")  # noqa: F821
