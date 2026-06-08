"""Entidad Tier 3: productos — TABLA ORM.

Definición de tabla pura: columnas + relationships `marca`/`moneda` + `get_by_id`. El filtrado
(`search`), la creación con find-or-create de catálogos (`marca`, `vehiculos`, `categorias`) y la
vinculación de sus relaciones, y el soft-delete viven en `producto_service.py` (+ `core/resolvers.py`);
el modelo no filtra ni orquesta.

Notas de contrato (resueltas en la capa service):
- `precio` se almacena en centavos en la moneda original (`moneda_id`, default 1 = MXN); la respuesta
  lo convierte a MXN.
- `create` resuelve por find-or-create `marca`/`vehiculos` (cascada marca)/`categorias` y, con éxito
  parcial, `ciudades` ({ciudad, estado}), escribiendo las tablas de relación.
"""

from sqlalchemy import ForeignKey, Integer, JSON, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.mixins import TimestampMixin
from app.database import Base
from app.models.marca_model import MarcaModel
from app.models.moneda_model import MonedaModel


class ProductoModel(TimestampMixin, Base):
    __tablename__ = "productos"

    marca_id: Mapped[int] = mapped_column(ForeignKey("marcas.id"), nullable=False)
    modelo: Mapped[str] = mapped_column(String(255), nullable=False)
    precio: Mapped[int] = mapped_column(Integer, nullable=False)
    moneda_id: Mapped[int] = mapped_column(ForeignKey("monedas.id"), nullable=False, default=1)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    especificaciones: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    marca: Mapped["MarcaModel"] = relationship(lazy="joined")
    moneda: Mapped["MonedaModel"] = relationship(lazy="joined")  # noqa: F821

    @classmethod
    def get_by_id(cls, db: Session, producto_id: int) -> "ProductoModel | None":
        """Producto activo por id, o None."""
        return db.scalar(select(cls).where(cls.id == producto_id, cls.deleted_at.is_(None)))
