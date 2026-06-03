"""Catálogo Tier 2: marcas. Crece solo por find-or-create.

El valor `marca` se almacena ya normalizado (lowercase/trim/sin acentos) y es UNIQUE.
"""

from sqlalchemy import String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.mixins import TimestampMixin, _now
from app.core.normalization import normalize
from app.database import Base


class MarcaModel(TimestampMixin, Base):
    __tablename__ = "marcas"
    __table_args__ = (UniqueConstraint("marca", name="uq_marcas_marca"),)

    marca: Mapped[str] = mapped_column(String(255), nullable=False)

    @classmethod
    def get_all(cls, db: Session) -> list["MarcaModel"]:
        return list(db.scalars(select(cls).where(cls.deleted_at.is_(None))))

    @classmethod
    def get_by_id(cls, db: Session, marca_id: int) -> "MarcaModel | None":
        return db.scalar(select(cls).where(cls.id == marca_id, cls.deleted_at.is_(None)))

    @classmethod
    def create(cls, db: Session, *, marca: str) -> "MarcaModel":
        ts = _now()
        row = cls(marca=normalize(marca), created_at=ts, updated_at=ts)
        db.add(row)
        db.flush()
        return row
