"""Catálogo Tier 1: monedas — TABLA ORM. Sin delete (catálogo; poblado por seeder).

`tipo_de_cambio` se almacena en centavos relativos a MXN (MXN=100, USD=1700, EUR=2300):
`mxn_centavos = round(precio * tipo_de_cambio / 100)`. El modelo solo expone `get_by_id`.
"""

from sqlalchemy import Integer, String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class MonedaModel(TimestampMixin, Base):
    __tablename__ = "monedas"
    __table_args__ = (UniqueConstraint("abreviacion", name="uq_monedas_abreviacion"),)

    moneda: Mapped[str] = mapped_column(String(255), nullable=False)
    abreviacion: Mapped[str] = mapped_column(String(10), nullable=False)
    tipo_de_cambio: Mapped[int] = mapped_column(Integer, nullable=False)

    @classmethod
    def get_by_id(cls, db: Session, moneda_id: int) -> "MonedaModel | None":
        return db.scalar(select(cls).where(cls.id == moneda_id, cls.deleted_at.is_(None)))
