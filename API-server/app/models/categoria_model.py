"""Catálogo Tier 2: categorias. Sin métodos (pendiente). Crece solo por find-or-create.

El valor `categoria` se almacena ya normalizado (lowercase/trim/sin acentos) y es UNIQUE.
"""

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class CategoriaModel(TimestampMixin, Base):
    __tablename__ = "categorias"
    __table_args__ = (UniqueConstraint("categoria", name="uq_categorias_categoria"),)

    categoria: Mapped[str] = mapped_column(String(255), nullable=False)
