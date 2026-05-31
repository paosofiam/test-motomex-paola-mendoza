"""Catálogo Tier 2: vehiculos. Sin métodos (pendiente). Crece solo por find-or-create.

Identidad: UNIQUE compuesto (modelo, marca_id, anio) — Versa Nissan 2015 ≠ 2016.
`modelo` se almacena normalizado. La relación `marca` (solo mapeo) permite exponer
el vehículo como objeto `{modelo, marca, anio}`.
"""

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampMixin
from app.database import Base


class VehiculoModel(TimestampMixin, Base):
    __tablename__ = "vehiculos"
    __table_args__ = (
        UniqueConstraint("modelo", "marca_id", "anio", name="uq_vehiculos_modelo_marca_anio"),
    )

    modelo: Mapped[str] = mapped_column(String(255), nullable=False)
    marca_id: Mapped[int] = mapped_column(ForeignKey("marcas.id"), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)

    marca: Mapped["MarcaModel"] = relationship(lazy="joined")  # noqa: F821
