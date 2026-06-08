"""Catálogo Tier 2: categorias — TABLA ORM. Crece solo por find-or-create.

El valor `categoria` se almacena ya normalizado (lowercase/trim/sin acentos) y es UNIQUE. La creación
con normalización vive en `core/resolvers.find_or_create_categoria`; el modelo solo expone `get_by_id`.
"""

from sqlalchemy import String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class CategoriaModel(TimestampMixin, Base):
    __tablename__ = "categorias"
    __table_args__ = (UniqueConstraint("categoria", name="uq_categorias_categoria"),)

    categoria: Mapped[str] = mapped_column(String(255), nullable=False)

    @classmethod
    def get_by_id(cls, db: Session, categoria_id: int) -> "CategoriaModel | None":
        return db.scalar(select(cls).where(cls.id == categoria_id, cls.deleted_at.is_(None)))
