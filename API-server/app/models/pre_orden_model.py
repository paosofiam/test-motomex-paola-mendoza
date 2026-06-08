"""Entidad Tier 3: pre_ordenes — TABLA ORM.

Definición de tabla pura: columnas + relationship `pre_orden_productos`, sin métodos. La creación
(header + líneas `pre_orden_productos`) vive en `pre_orden_service.py`.

`total` se persiste en MXN ya convertido (centavos). NO lleva `moneda_id`. El agente calcula el total
consultando GET /productos (que ya devuelve precios en MXN) y envía el total convertido en el body;
el service lo persiste sin recalcular.
"""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins import TimestampMixin
from app.database import Base
from app.models.pre_orden_producto_model import PreOrdenProductoModel


class PreOrdenModel(TimestampMixin, Base):
    __tablename__ = "pre_ordenes"

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)

    pre_orden_productos: Mapped[list["PreOrdenProductoModel"]] = relationship(
        primaryjoin=lambda: (PreOrdenModel.id == PreOrdenProductoModel.pre_orden_id)
        & (PreOrdenProductoModel.deleted_at.is_(None)),
        viewonly=True,
        lazy="selectin",
    )
