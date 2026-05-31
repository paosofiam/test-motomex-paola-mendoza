"""Catálogo Tier 1: intenciones_de_compra_de_leads. Sin métodos (pendiente). Sin delete."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class IntencionDeCompraDeLeadModel(TimestampMixin, Base):
    __tablename__ = "intenciones_de_compra_de_leads"

    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
