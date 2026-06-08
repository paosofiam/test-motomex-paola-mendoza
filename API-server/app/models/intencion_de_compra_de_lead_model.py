"""Catálogo Tier 1: intenciones_de_compra_de_leads — TABLA ORM. Sin delete (poblado por seeder).

El modelo solo expone `get_by_id`.
"""

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class IntencionDeCompraDeLeadModel(TimestampMixin, Base):
    __tablename__ = "intenciones_de_compra_de_leads"

    tipo: Mapped[str] = mapped_column(String(50), nullable=False)

    @classmethod
    def get_by_id(cls, db: Session, intencion_id: int) -> "IntencionDeCompraDeLeadModel | None":
        return db.scalar(select(cls).where(cls.id == intencion_id, cls.deleted_at.is_(None)))
