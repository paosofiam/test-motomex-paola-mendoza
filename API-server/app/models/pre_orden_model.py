"""Entidad Tier 3: pre_ordenes — MODELO FUNCIONAL.

Métodos permitidos (matriz): create (único).

`total` se persiste en MXN ya convertido (centavos). NO lleva `moneda_id`.
El agente calcula el total consultando GET /productos (que ya devuelve precios en MXN)
y envía el total convertido en el body; el modelo lo persiste sin recalcular.
"""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.mixins import TimestampMixin, _now
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

    @classmethod
    def create(
        cls,
        db: Session,
        *,
        lead_id: int,
        total: int,
        productos: list[dict],
    ) -> "PreOrdenModel":
        """Crea una pre-orden con sus líneas de producto.

        Cada ítem de `productos` es un dict `{"producto_id": int, "cantidad": int}`.
        Solo consulta/inserta en BD. La validación de existencia de `lead_id` y de cada
        `producto_id` vive en la capa service (`pre_orden_service.create`), que lanza
        `NotFoundError` antes de invocar este método.
        `total` se recibe ya en MXN centavos (el agente lo calcula previamente).
        `created_at == updated_at` (mismo ts). Hace flush y devuelve la instancia
        con pre_orden_productos cargados (selectin) para que el service construya
        la respuesta.
        """
        ts = _now()
        pre_orden = cls(lead_id=lead_id, total=total, created_at=ts, updated_at=ts)
        db.add(pre_orden)
        db.flush()

        db.add_all([
            PreOrdenProductoModel(
                pre_orden_id=pre_orden.id,
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                created_at=ts,
                updated_at=ts,
            )
            for item in productos
        ])
        db.flush()
        db.refresh(pre_orden)
        return pre_orden
