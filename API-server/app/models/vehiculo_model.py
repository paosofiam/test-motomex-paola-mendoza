"""Catálogo Tier 2: vehiculos — TABLA ORM. Crece solo por find-or-create.

Identidad: UNIQUE compuesto (modelo, marca_id, anio) — Versa Nissan 2015 ≠ 2016. `modelo` se
almacena normalizado. La relación `marca` (solo mapeo) permite exponer el vehículo como objeto
`{modelo, marca, anio}`. La creación (normalización + cascada marca) vive en
`core/resolvers.find_or_create_vehiculo`; el modelo solo expone `get_by_id`.
"""

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

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

    @classmethod
    def get_by_id(cls, db: Session, vehiculo_id: int) -> "VehiculoModel | None":
        return db.scalar(select(cls).where(cls.id == vehiculo_id, cls.deleted_at.is_(None)))
