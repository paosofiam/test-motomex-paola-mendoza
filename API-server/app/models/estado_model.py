"""Catálogo Tier 1: estados. Sin métodos (pendiente). Sin delete (catálogo)."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class EstadoModel(TimestampMixin, Base):
    __tablename__ = "estados"

    estado: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
