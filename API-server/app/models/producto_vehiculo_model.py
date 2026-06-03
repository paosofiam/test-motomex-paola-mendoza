"""Tabla de relación N:M productos_vehiculos (compatibilidades). Sin métodos propios: las filas se gestionan desde ProductoModel.

Columnas estándar + 2 FKs + UNIQUE(producto_id, vehiculo_id) para evitar duplicados.
"""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class ProductoVehiculoModel(TimestampMixin, Base):
    __tablename__ = "productos_vehiculos"
    __table_args__ = (
        UniqueConstraint("producto_id", "vehiculo_id", name="uq_productos_vehiculos"),
    )

    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    vehiculo_id: Mapped[int] = mapped_column(ForeignKey("vehiculos.id"), nullable=False)
