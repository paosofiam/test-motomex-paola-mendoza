"""Catálogo Tier 2: categorias. Crece solo por find-or-create.

El valor `categoria` se almacena ya normalizado (lowercase/trim/sin acentos) y es UNIQUE.
"""

from sqlalchemy import String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.mixins import TimestampMixin, _now
from app.core.normalization import normalize
from app.database import Base


class CategoriaModel(TimestampMixin, Base):
    __tablename__ = "categorias"
    __table_args__ = (UniqueConstraint("categoria", name="uq_categorias_categoria"),)

    categoria: Mapped[str] = mapped_column(String(255), nullable=False)

    # ---- Métodos de la matriz -------------------------------------------------

    @classmethod
    def get_all(cls, db: Session) -> list["CategoriaModel"]:
        return list(db.scalars(select(cls).where(cls.deleted_at.is_(None))))

    @classmethod
    def get_by_id(cls, db: Session, categoria_id: int) -> "CategoriaModel | None":
        return db.scalar(select(cls).where(cls.id == categoria_id, cls.deleted_at.is_(None)))

    @classmethod
    def create(cls, db: Session, *, categoria: str) -> "CategoriaModel":
        ts = _now()
        row = cls(categoria=normalize(categoria), created_at=ts, updated_at=ts)
        db.add(row)
        db.flush()
        return row
