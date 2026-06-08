"""Catálogo Tier 1: estados — COMPLETO. Sin métodos por diseño.

No figura en la matriz de CLAUDE.md (cero métodos permitidos). Sin endpoint GET /estados
(Tier 1 estático; el LLM conoce las 32 entidades federativas mexicanas vía system prompt).
`abreviacion` permite resolver el estado por nombre o por su clave corta (p. ej. "Nuevo León"
o "NL") cuando una ciudad lo transporta en el body; la resolución vive en la capa service.
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
    abreviacion: Mapped[str | None] = mapped_column(String(10), nullable=True)
