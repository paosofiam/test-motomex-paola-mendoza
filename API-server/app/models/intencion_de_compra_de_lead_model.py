"""Catálogo Tier 1: intenciones_de_compra_de_leads. Sin delete."""

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.mixins import TimestampMixin, _now
from app.database import Base


class IntencionDeCompraDeLeadModel(TimestampMixin, Base):
    __tablename__ = "intenciones_de_compra_de_leads"

    tipo: Mapped[str] = mapped_column(String(50), nullable=False)

    # ---- Métodos de la matriz -------------------------------------------------

    @classmethod
    def get_all(cls, db: Session) -> list["IntencionDeCompraDeLeadModel"]:
        return list(db.scalars(select(cls).where(cls.deleted_at.is_(None))))

    @classmethod
    def get_by_id(cls, db: Session, intencion_id: int) -> "IntencionDeCompraDeLeadModel | None":
        return db.scalar(select(cls).where(cls.id == intencion_id, cls.deleted_at.is_(None)))

    @classmethod
    def create(cls, db: Session, *, tipo: str) -> "IntencionDeCompraDeLeadModel":
        ts = _now()
        row = cls(tipo=tipo, created_at=ts, updated_at=ts)
        db.add(row)
        db.flush()
        return row
