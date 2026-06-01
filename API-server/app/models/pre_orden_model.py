"""Entidad Tier 3: pre_ordenes — MODELO FUNCIONAL.

Métodos permitidos (matriz): create (único).

`total` se persiste en MXN ya convertido (centavos). NO lleva `moneda_id`.
El agente calcula el total consultando GET /productos (que ya devuelve precios en MXN)
y envía el total convertido en el body; el modelo lo persiste sin recalcular.
"""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.exceptions import NotFoundError
from app.core.mixins import TimestampMixin, _now
from app.database import Base
from app.models.pre_orden_producto_model import PreOrdenProductoModel


class PreOrdenModel(TimestampMixin, Base):
    __tablename__ = "pre_ordenes"

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)  # centavos, MXN

    pre_orden_productos: Mapped[list["PreOrdenProductoModel"]] = relationship(
        primaryjoin=lambda: (PreOrdenModel.id == PreOrdenProductoModel.pre_orden_id)
        & (PreOrdenProductoModel.deleted_at.is_(None)),
        viewonly=True,
        lazy="selectin",
    )

    # ---- Métodos de la matriz -------------------------------------------------

    @classmethod
    def create(
        cls,
        db: Session,
        *,
        lead_id: int,
        total: int,
        productos: list[dict],  # [{"producto_id": int, "cantidad": int}]
    ) -> "PreOrdenModel":
        """Crea una pre-orden con sus líneas de producto.

        Valida lead_id y cada producto_id (find-or-fail → NotFoundError → 404).
        `total` se recibe ya en MXN centavos (el agente lo calcula previamente).
        `created_at == updated_at` (mismo ts). Hace flush y devuelve la instancia
        con pre_orden_productos cargados (selectin) para que el service construya
        la respuesta.
        """
        # Deferred: LeadModel importa resolvers; defensivo ante cambios futuros
        from app.models.lead_model import LeadModel
        from app.models.producto_model import ProductoModel

        if LeadModel.get_by_id(db, lead_id) is None:
            raise NotFoundError("Lead", lead_id)
        for item in productos:
            if ProductoModel.get_by_id(db, item["producto_id"]) is None:
                raise NotFoundError("Producto", item["producto_id"])

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

    # PENDIENTE service (pre_orden_service.py):
    #   from app.schemas.pre_orden import PreOrdenCreate, PreOrdenProductoResponse, PreOrdenResponse
    #
    #   def _to_response(pre_orden: PreOrdenModel) -> PreOrdenResponse:
    #       return PreOrdenResponse(
    #           id=pre_orden.id, lead_id=pre_orden.lead_id, total=pre_orden.total,
    #           productos=[
    #               PreOrdenProductoResponse(
    #                   producto_id=linea.producto_id,
    #                   modelo=linea.producto.modelo,   # lazy="joined" en PreOrdenProductoModel
    #                   cantidad=linea.cantidad,
    #               )
    #               for linea in pre_orden.pre_orden_productos  # lazy="selectin"
    #           ],
    #       )
    #
    #   def create(db, payload: PreOrdenCreate) -> PreOrdenResponse:
    #       pre_orden = PreOrdenModel.create(
    #           db, lead_id=payload.lead_id, total=payload.total,
    #           productos=[p.model_dump() for p in payload.productos],
    #       )
    #       return _to_response(pre_orden)
    #
    # NOTA: PreOrdenResponse.from_attributes=True pero 'productos' no mapea automáticamente
    # (atributo ORM = pre_orden_productos ≠ productos; modelo no es columna directa).
    # La construcción manual en _to_response es obligatoria.
