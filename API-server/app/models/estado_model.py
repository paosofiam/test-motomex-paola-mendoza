"""Catálogo Tier 1: estados. Sin métodos (pendiente). Sin delete (catálogo)."""

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class EstadoModel(TimestampMixin, Base):
    __tablename__ = "estados"
    __table_args__ = (UniqueConstraint("estado", name="uq_estados_estado"),)

    estado: Mapped[str] = mapped_column(String(255), nullable=False)
