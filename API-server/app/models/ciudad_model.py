"""Catálogo Tier 2: ciudades — TABLA ORM. Crece solo por find-or-create.

`ciudad` se almacena normalizado y es UNIQUE. `estado_id` es NOT NULL: toda ciudad pertenece a un
estado (de ahí se deriva el campo de respuesta `leads.estado`). La relación `estado` (solo mapeo)
habilita esa derivación. La creación (normalización + estado requerido) vive en
`core/resolvers.find_or_create_ciudad`; el modelo solo expone `get_by_id`.
"""

from sqlalchemy import ForeignKey, String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.mixins import TimestampMixin
from app.database import Base


class CiudadModel(TimestampMixin, Base):
    __tablename__ = "ciudades"
    __table_args__ = (UniqueConstraint("ciudad", name="uq_ciudades_ciudad"),)

    ciudad: Mapped[str] = mapped_column(String(255), nullable=False)
    estado_id: Mapped[int] = mapped_column(ForeignKey("estados.id"), nullable=False)

    estado: Mapped["EstadoModel"] = relationship(lazy="joined")  # noqa: F821

    @classmethod
    def get_by_id(cls, db: Session, ciudad_id: int) -> "CiudadModel | None":
        return db.scalar(select(cls).where(cls.id == ciudad_id, cls.deleted_at.is_(None)))
