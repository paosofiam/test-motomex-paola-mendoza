"""Capa de orquestación del recurso pre_ordenes (router → service → model).

Media entre `routers/pre_ordenes.py` y `PreOrdenModel`: recibe los schemas ya validados por
Pydantic, valida la existencia de los ids referenciados (find-or-fail Tier 3, sin resolución por
string) y construye el `PreOrdenResponse` que el router devuelve por HTTP. No conoce FastAPI ni
gestiona la transacción (el commit lo hace `get_db`); solo lanza excepciones de dominio
(`NotFoundError`), que `core/error_handlers.py` traduce a RFC 7807.

Construcción de la respuesta (`endpoints.md`): `total` se devuelve tal cual (ya en MXN centavos,
persistido por el modelo; NO se reconvierte) y cada ítem expone `modelo` derivado de
`producto.modelo`.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.lead_model import LeadModel
from app.models.pre_orden_model import PreOrdenModel
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
    """Crea una pre-orden. Valida `lead_id` y cada `producto_id` exacto (Tier 3, sin resolución por
    string ni find-or-create) → `NotFoundError` (→ 404) si no existe o está soft-deleted. `total`
    se persiste tal cual (ya en MXN centavos; el agente LLM lo calcula previamente).
    """
    if LeadModel.get_by_id(db, payload.lead_id) is None:
        raise NotFoundError("Lead", payload.lead_id)
    for item in payload.productos:
        if ProductoModel.get_by_id(db, item.producto_id) is None:
            raise NotFoundError("Producto", item.producto_id)

    pre_orden = PreOrdenModel.create(
        db,
        lead_id=payload.lead_id,
        total=payload.total,
        productos=[item.model_dump() for item in payload.productos],
    )
    return _to_response(pre_orden)
