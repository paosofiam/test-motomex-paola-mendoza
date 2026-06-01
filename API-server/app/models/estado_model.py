"""Catálogo Tier 1: estados — COMPLETO. Sin métodos por diseño.

No figura en la matriz de CLAUDE.md (cero métodos permitidos). Sin endpoint GET /estados
(Tier 1 estático; el LLM conoce los 32 estados mexicanos vía system prompt).
El campo `leads.estado` en respuestas se deriva vía acceso de atributo: `lead.ciudad.estado.estado`;
funciona porque CiudadModel.estado es relationship(lazy="joined") — sin queries extra.
Sin delete (catálogo; crece solo por seeder).
"""

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class EstadoModel(TimestampMixin, Base):
    __tablename__ = "estados"
    __table_args__ = (UniqueConstraint("estado", name="uq_estados_estado"),)

    estado: Mapped[str] = mapped_column(String(255), nullable=False)
