"""Catálogo Tier 2: ciudades. Sin métodos (pendiente). Crece solo por find-or-create.

`ciudad` se almacena normalizado y es UNIQUE. `estado_id` es NOT NULL: toda ciudad
pertenece a un estado (de ahí se deriva el campo de respuesta `leads.estado`).
La relación `estado` (solo mapeo, sin métodos) habilita esa derivación.
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampMixin
from app.database import Base


class CiudadModel(TimestampMixin, Base):
    __tablename__ = "ciudades"

    ciudad: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    estado_id: Mapped[int] = mapped_column(ForeignKey("estados.id"), nullable=False)

    estado: Mapped["EstadoModel"] = relationship(lazy="joined")  # noqa: F821
