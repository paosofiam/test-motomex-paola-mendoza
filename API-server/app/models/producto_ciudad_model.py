"""Tabla de relación N:M productos_ciudades. Sin métodos (pendiente).

Columnas estándar + 2 FKs + UNIQUE(producto_id, ciudad_id).
"""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class ProductoCiudadModel(TimestampMixin, Base):
    __tablename__ = "productos_ciudades"
    __table_args__ = (
        UniqueConstraint("producto_id", "ciudad_id", name="uq_productos_ciudades"),
    )

    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    ciudad_id: Mapped[int] = mapped_column(ForeignKey("ciudades.id"), nullable=False)
