"""Catálogo Tier 1: monedas. Sin métodos (pendiente). Sin delete (catálogo)."""

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class MonedaModel(TimestampMixin, Base):
    __tablename__ = "monedas"
    __table_args__ = (UniqueConstraint("abreviacion", name="uq_monedas_abreviacion"),)

    moneda: Mapped[str] = mapped_column(String(255), nullable=False)
    abreviacion: Mapped[str] = mapped_column(String(10), nullable=False)
    tipo_de_cambio: Mapped[int] = mapped_column(Integer, nullable=False)  # centavos vs MXN
