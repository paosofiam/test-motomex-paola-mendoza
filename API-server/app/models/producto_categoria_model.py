"""Tabla de relación N:M productos_categorias. Sin métodos (pendiente).

Columnas estándar + 2 FKs + UNIQUE(producto_id, categoria_id).
"""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class ProductoCategoriaModel(TimestampMixin, Base):
    __tablename__ = "productos_categorias"
    __table_args__ = (
        UniqueConstraint("producto_id", "categoria_id", name="uq_productos_categorias"),
    )

    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)
