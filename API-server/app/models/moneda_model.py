"""Catálogo Tier 1: monedas. Sin métodos (pendiente). Sin delete (catálogo)."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class MonedaModel(TimestampMixin, Base):
    __tablename__ = "monedas"

    moneda: Mapped[str] = mapped_column(String(255), nullable=False)
    abreviacion: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    tipo_de_cambio: Mapped[int] = mapped_column(Integer, nullable=False)  # centavos vs MXN
