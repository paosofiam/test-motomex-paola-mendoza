"""Catálogo Tier 2: categorias. Sin métodos (pendiente). Crece solo por find-or-create.

El valor `categoria` se almacena ya normalizado (lowercase/trim/sin acentos) y es UNIQUE.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class CategoriaModel(TimestampMixin, Base):
    __tablename__ = "categorias"

    categoria: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
