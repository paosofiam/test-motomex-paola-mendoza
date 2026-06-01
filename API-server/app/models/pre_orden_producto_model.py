"""Tabla de relación N:M pre_ordenes_productos.

Columnas estándar + 2 FKs + `cantidad` (Integer NOT NULL) + UNIQUE(pre_orden_id, producto_id):
una sola fila por (pre_orden, producto) consolidando N unidades.
La relación `producto` (lazy="joined") permite acceder a `producto.modelo` desde el service
sin query extra al construir PreOrdenResponse.
"""

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampMixin
from app.database import Base
from app.models.producto_model import ProductoModel


class PreOrdenProductoModel(TimestampMixin, Base):
    __tablename__ = "pre_ordenes_productos"
    __table_args__ = (
        UniqueConstraint("pre_orden_id", "producto_id", name="uq_pre_ordenes_productos"),
    )

    pre_orden_id: Mapped[int] = mapped_column(ForeignKey("pre_ordenes.id"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)

    producto: Mapped["ProductoModel"] = relationship(lazy="joined")
