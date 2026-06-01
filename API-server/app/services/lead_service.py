"""Capa de orquestación del recurso leads (router → service → model).

Media entre `routers/leads.py` y `LeadModel`: recibe los schemas ya validados por Pydantic, llama
a los métodos de la matriz del modelo y construye el `LeadResponse` que el router devuelve por HTTP.
No conoce FastAPI ni gestiona la transacción (el commit lo hace `get_db`); solo lanza excepciones
de dominio (`NotFoundError`/`ResolutionError`), que `core/error_handlers.py` traduce a RFC 7807.

Construcción de la respuesta (`endpoints.md`): incluye los campos derivados `chat_id`
(chat activo más reciente, vía `resolvers.get_active_chat_id`), `estado`
(`ciudad → ciudades.estado_id → estados.estado`) e `intencion_de_compra` (string). Los vehículos
viajan siempre como objetos `{modelo, marca, anio}`.
"""

from sqlalchemy.orm import Session

from app.core import resolvers
from app.core.exceptions import NotFoundError
from app.models.lead_model import LeadModel
from app.schemas.common import VehiculoSchema
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate


def _to_response(db: Session, lead: LeadModel) -> LeadResponse:
    """Convierte la instancia ORM al DTO de respuesta, resolviendo los campos derivados."""
    return LeadResponse(
        id=lead.id,
        chat_id=resolvers.get_active_chat_id(db, lead.id),
        chat_whatsapp_id=lead.chat_whatsapp_id,
        nombre_whatsapp=lead.nombre_whatsapp,
        telefono=lead.telefono,
        nombre=lead.nombre,
        ciudad=lead.ciudad.ciudad if lead.ciudad else None,
        estado=lead.ciudad.estado.estado if lead.ciudad else None,
        productos_interes=[lp.producto.modelo for lp in lead.leads_productos],
        vehiculo=[
            VehiculoSchema(
                modelo=lv.vehiculo.modelo,
                marca=lv.vehiculo.marca.marca,
                anio=lv.vehiculo.anio,
            )
            for lv in lead.leads_vehiculos
        ],
        direccion_envio=lead.direccion_envio,
        intencion_de_compra=lead.intencion.tipo,
    )


def search(
    db: Session,
    chat_whatsapp_id: str | None = None,
    intencion_de_compra: str | None = None,
) -> list[LeadResponse]:
    """Lista leads activos, con filtros opcionales por `chat_whatsapp_id` e `intencion_de_compra`."""
    leads = LeadModel.search(
        db, chat_whatsapp_id=chat_whatsapp_id, intencion_de_compra=intencion_de_compra
    )
    return [_to_response(db, lead) for lead in leads]


def get_by_id(db: Session, lead_id: int) -> LeadResponse:
    """Lead activo por id. Lanza `NotFoundError` (→ 404) si no existe o está soft-deleted."""
    lead = LeadModel.get_by_id(db, lead_id)
    if lead is None:
        raise NotFoundError("Lead", lead_id)
    return _to_response(db, lead)


def create(db: Session, payload: LeadCreate) -> LeadResponse:
    """Crea un lead. `ciudad`/`productos_interes` find-or-fail; `vehiculo` find-or-create.
    `model_dump()` convierte `vehiculo` a `list[dict]`; los campos coinciden con los kwargs de `create`.
    """
    lead = LeadModel.create(db, **payload.model_dump())
    return _to_response(db, lead)


def update(db: Session, lead_id: int, payload: LeadUpdate) -> LeadResponse:
    """Actualización parcial (PATCH). `exclude_unset=True` pasa solo los campos enviados, alineado
    con el sentinel `_UNSET` de `LeadModel.update` (que ya lanza `NotFoundError` si no existe).
    """
    lead = LeadModel.update(db, lead_id, **payload.model_dump(exclude_unset=True))
    return _to_response(db, lead)
