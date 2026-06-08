"""Capa de orquestación del recurso pre_ordenes (router → service → model).

Media entre `routers/pre_ordenes.py` y `PreOrdenModel` (tabla ORM pura): recibe los schemas ya
validados por Pydantic, valida la existencia de los ids referenciados (find-or-fail Tier 3, sin
resolución por string), crea la pre-orden con sus líneas y construye el `PreOrdenResponse` que el
router devuelve por HTTP. No conoce FastAPI ni gestiona la transacción (el commit lo hace `get_db`);
solo lanza excepciones de dominio (`NotFoundError`), que `core/error_handlers.py` traduce a RFC 7807.

Construcción de la respuesta (`endpoints.md`): `total` se devuelve tal cual (ya en MXN centavos; NO
se reconvierte) y cada ítem expone `modelo` derivado de `producto.modelo`.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.mixins import _now
from app.models.lead_model import LeadModel
from app.models.pre_orden_model import PreOrdenModel
from app.models.pre_orden_producto_model import PreOrdenProductoModel
from app.models.producto_model import ProductoModel
from app.schemas.pre_orden import PreOrdenCreate, PreOrdenProductoResponse, PreOrdenResponse


def _to_response(pre_orden: PreOrdenModel) -> PreOrdenResponse:
    """Convierte la instancia ORM al DTO de respuesta. `total` ya viene en MXN centavos; cada línea
    expone `modelo` vía `linea.producto` (lazy="joined" en `PreOrdenProductoModel`)."""
    return PreOrdenResponse(
        id=pre_orden.id,
        lead_id=pre_orden.lead_id,
        total=pre_orden.total,
        productos=[
            PreOrdenProductoResponse(
                producto_id=linea.producto_id,
                modelo=linea.producto.modelo,
                cantidad=linea.cantidad,
            )
            for linea in pre_orden.pre_orden_productos
        ],
    )


def create(db: Session, payload: PreOrdenCreate) -> PreOrdenResponse:
    """Crea una pre-orden con sus líneas. Valida `lead_id` y cada `producto_id` exacto (Tier 3, sin
    resolución por string ni find-or-create) → `NotFoundError` (→ 404) si no existe o está
    soft-deleted. `total` se persiste tal cual (ya en MXN centavos; el agente LLM lo calcula
    previamente). `created_at == updated_at`.

    `db.flush()` de las líneas ANTES del `db.refresh(pre_orden)`: sin esto, con `autoflush=False`, la
    carga `selectin` de `pre_orden_productos` leería la tabla aún vacía y la respuesta saldría sin
    líneas.
    """
    if LeadModel.get_by_id(db, payload.lead_id) is None:
        raise NotFoundError("Lead", payload.lead_id)
    for item in payload.productos:
        if ProductoModel.get_by_id(db, item.producto_id) is None:
            raise NotFoundError("Producto", item.producto_id)

    ts = _now()
    pre_orden = PreOrdenModel(lead_id=payload.lead_id, total=payload.total, created_at=ts, updated_at=ts)
    db.add(pre_orden)
    db.flush()

    db.add_all([
        PreOrdenProductoModel(
            pre_orden_id=pre_orden.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            created_at=ts,
            updated_at=ts,
        )
        for item in payload.productos
    ])
    db.flush()
    db.refresh(pre_orden)
    return _to_response(pre_orden)
