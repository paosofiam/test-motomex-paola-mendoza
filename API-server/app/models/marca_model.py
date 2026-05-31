"""Catálogo Tier 2: marcas. Sin métodos (pendiente). Crece solo por find-or-create.

El valor `marca` se almacena ya normalizado (lowercase/trim/sin acentos) y es UNIQUE.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class MarcaModel(TimestampMixin, Base):
    __tablename__ = "marcas"

    marca: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
