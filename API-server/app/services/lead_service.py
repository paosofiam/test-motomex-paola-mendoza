"""Capa de orquestación del recurso leads (router → service → model).

Media entre `routers/leads.py` y `LeadModel` (tabla ORM pura): recibe los schemas ya validados por
Pydantic, construye las queries/escrituras (filtrado de `search`, INSERT/UPDATE del lead y
reconciliación de sus tablas de relación vía `resolvers.sync_link_rows`) y arma el `LeadResponse`
que el router devuelve por HTTP. No conoce FastAPI ni gestiona la transacción (el commit lo hace
`get_db`); solo lanza excepciones de dominio (`NotFoundError`/`ResolutionError`), que
`core/error_handlers.py` traduce a RFC 7807.

Construcción de la respuesta (`endpoints.md`): incluye los campos derivados `chat_id` y `status`
(chat activo más reciente, vía `resolvers.get_active_chat`), `estado` (`ciudad → ciudades.estado_id →
estados.estado`) e `intencion_de_compra` (string). `lead_id` se devuelve además del `id` como alias
informativo (identificador cruzado, simétrico con `Chat`). Los vehículos viajan siempre como objetos
`{modelo, marca, anio}`.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import resolvers
from app.core.exceptions import NotFoundError, ResolutionError
from app.core.mixins import _now
from app.models.intencion_de_compra_de_lead_model import IntencionDeCompraDeLeadModel
from app.models.lead_model import LeadModel
from app.models.lead_producto_model import LeadProductoModel
from app.models.lead_vehiculo_model import LeadVehiculoModel
from app.schemas.common import VehiculoSchema
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate


def _validate_intencion(db: Session, intencion_de_compra_id: int) -> None:
    """`intencion_de_compra_id` es Tier 1 (catálogo): id que no resuelve → `ResolutionError`
    (→ 422 con `field`/`value_received`), no una FK rota que daría un 500 opaco."""
    if IntencionDeCompraDeLeadModel.get_by_id(db, intencion_de_compra_id) is None:
        raise ResolutionError(field="intencion_de_compra_id", value_received=intencion_de_compra_id)


def _resolver_ciudad(db: Session, ciudad: dict | None) -> tuple[int | None, list[str]]:
    """Resuelve el objeto `{ciudad, estado}` del lead a `ciudad_id` con éxito parcial.

    Reutiliza `resolvers.resolver_ciudades` (lista de un elemento). Devuelve `(ciudad_id, avisos)`:
    si `ciudad` es None → `(None, [])`; si el estado no se reconoce → `(None, [aviso])` y el lead se
    guarda sin ciudad.
    """
    if not ciudad:
        return None, []
    resueltas, avisos = resolvers.resolver_ciudades(db, [ciudad])
    return (resueltas[0].id if resueltas else None), avisos


def _sync_productos_interes(
    db: Session,
    lead_id: int,
    productos_interes: list[str] | None,
    ts: datetime,
) -> list[str]:
    """Vincula `productos_interes` a `leads_productos` de forma ADITIVA (find-or-skip, éxito parcial).

    Un modelo puede matchear varios productos → se persisten todas las relaciones. Los modelos que no
    existen en el inventario se omiten y se devuelven como avisos (el lead se crea/edita igual; nunca
    se rechaza ni se crea inventario). Conserva los vínculos previos: vacío/`None` = sin cambios (no
    hay remoción vía API). Devuelve los avisos de los modelos omitidos.
    """
    if not productos_interes:
        return []
    producto_ids, avisos = resolvers.resolver_productos_interes(db, productos_interes)
    resolvers.sync_link_rows(
        db, LeadProductoModel, "lead_id", lead_id, "producto_id", producto_ids, ts
    )
    return avisos


def _sync_vehiculos(
    db: Session,
    lead_id: int,
    vehiculo: list[dict] | None,
    ts: datetime,
) -> None:
    """Vincula `vehiculo` [{modelo,marca,anio}] a `leads_vehiculos` de forma ADITIVA (find-or-create,
    cascada marca). Conserva los vínculos previos: vacío/`None` = sin cambios (no hay remoción)."""
    if not vehiculo:
        return
    vehiculo_ids = [
        resolvers.find_or_create_vehiculo(db, v["modelo"], v["marca"], v["anio"]).id
        for v in vehiculo
    ]
    resolvers.sync_link_rows(
        db, LeadVehiculoModel, "lead_id", lead_id, "vehiculo_id", vehiculo_ids, ts
    )


def _get_active_by_chat_whatsapp_id(db: Session, chat_whatsapp_id: str) -> LeadModel | None:
    """Lead activo más reciente por `chat_whatsapp_id` (ORDER BY created_at DESC LIMIT 1).

    Espejo de `chat_service._get_by_chat_whatsapp_id`. Es la clave de unicidad de leads: lo usan la
    idempotencia de `create` y la consulta `get_by_chat_whatsapp_id`.
    """
    return db.scalar(
        select(LeadModel)
        .where(LeadModel.chat_whatsapp_id == chat_whatsapp_id, LeadModel.deleted_at.is_(None))
        .order_by(LeadModel.created_at.desc())
        .limit(1)
    )


def _to_response(db: Session, lead: LeadModel) -> LeadResponse:
    """Convierte la instancia ORM al DTO de respuesta, resolviendo los campos derivados."""
    chat = resolvers.get_active_chat(db, lead.id)
    return LeadResponse(
        id=lead.id,
        lead_id=lead.id,
        chat_id=chat.id if chat else None,
        status=chat.chat_status.status if chat else None,
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


def get_by_chat_whatsapp_id(db: Session, chat_whatsapp_id: str) -> LeadResponse:
    """Lead activo más reciente por `chat_whatsapp_id` (un solo objeto, calcando a chats).

    Por la regla "un lead activo por `chat_whatsapp_id`" la consulta retorna a lo sumo uno
    (`ORDER BY created_at DESC LIMIT 1`); lanza `NotFoundError` (→ 404) si no existe ninguno activo.
    """
    lead = _get_active_by_chat_whatsapp_id(db, chat_whatsapp_id)
    if lead is None:
        raise NotFoundError(
            "Lead",
            chat_whatsapp_id,
            detail=f"No existe un lead activo para chat_whatsapp_id={chat_whatsapp_id}",
        )
    return _to_response(db, lead)


def get_by_id(db: Session, lead_id: int) -> LeadResponse:
    """Lead activo por id. Lanza `NotFoundError` (→ 404) si no existe o está soft-deleted."""
    lead = LeadModel.get_by_id(db, lead_id)
    if lead is None:
        raise NotFoundError("Lead", lead_id)
    return _to_response(db, lead)


def create(db: Session, payload: LeadCreate) -> tuple[LeadResponse, list[str], bool]:
    """Crea un lead de forma IDEMPOTENTE por `chat_whatsapp_id`. Si ya existe un lead activo con ese
    `chat_whatsapp_id`, NO crea uno nuevo: ignora el body y devuelve el existente (el router responde
    200). Solo si no existe ninguno se valida y se crea (201). Los leads no se borran vía API: para
    enriquecer uno existente se usa `PATCH /leads/{id}` sobre su `id`.

    Cuando se crea: el lead SIEMPRE se guarda. `ciudad` ({ciudad, estado}) se resuelve a `ciudad_id`
    con éxito parcial; `productos_interes` es find-or-skip aditivo; `vehiculo` find-or-create. Si el
    estado de la ciudad no se reconoce o un producto de interés no existe en el inventario, se omite
    ese dato, el lead se guarda igual y se acumula el aviso (el router lo expone en el header
    `Warning`).

    `db.flush()` de las filas de relación ANTES del `db.refresh(lead)`: sin esto, con
    `autoflush=False`, la carga `selectin` de `leads_productos`/`leads_vehiculos` leería las tablas
    de relación aún vacías y la respuesta saldría con listas vacías. `created_at == updated_at`.

    Devuelve `(respuesta, avisos, creado)`: `creado=False` (y `avisos=[]`) cuando se devolvió uno ya
    existente.
    """
    existente = _get_active_by_chat_whatsapp_id(db, payload.chat_whatsapp_id)
    if existente is not None:
        return _to_response(db, existente), [], False

    _validate_intencion(db, payload.intencion_de_compra_id)
    data = payload.model_dump()
    ciudad_id, avisos = _resolver_ciudad(db, data.pop("ciudad"))
    productos_interes = data.pop("productos_interes")
    vehiculo = data.pop("vehiculo")

    ts = _now()
    lead = LeadModel(**data, ciudad_id=ciudad_id, created_at=ts, updated_at=ts)
    db.add(lead)
    db.flush()

    avisos += _sync_productos_interes(db, lead.id, productos_interes, ts)
    _sync_vehiculos(db, lead.id, vehiculo, ts)

    db.flush()
    db.refresh(lead)
    return _to_response(db, lead), avisos, True


def update(db: Session, lead_id: int, payload: LeadUpdate) -> tuple[LeadResponse, list[str]]:
    """Actualización parcial (PATCH). `exclude_unset=True` aplica solo los campos enviados.
    `chat_whatsapp_id` es inmutable (no está en `LeadUpdate`). Refresca solo `updated_at`. Las
    relaciones (`productos_interes`, `vehiculo`) se vinculan de forma ADITIVA: combinan lo enviado con
    lo existente sin reemplazar ni borrar, y un body vacío/omitido las deja intactas (no hay remoción
    vía API). Lanza `NotFoundError` (→ 404) si el lead no existe o está soft-deleted. Si se envía
    `intencion_de_compra_id`, se valida como Tier 1 (→ `ResolutionError`/422) antes de tocar la BD. Si
    se envía `ciudad`, se resuelve a `ciudad_id` con éxito parcial; los modelos de `productos_interes`
    que no existan en inventario se omiten con aviso. Devuelve `(respuesta, avisos)`.

    Hace `db.flush()` ANTES de `db.refresh(lead)` por la misma razón de `create` (selectin).
    """
    cambios = payload.model_dump(exclude_unset=True)
    if cambios.get("intencion_de_compra_id") is not None:
        _validate_intencion(db, cambios["intencion_de_compra_id"])
    avisos: list[str] = []
    if "ciudad" in cambios:
        ciudad_id, avisos = _resolver_ciudad(db, cambios.pop("ciudad"))
        cambios["ciudad_id"] = ciudad_id

    lead = LeadModel.get_by_id(db, lead_id)
    if lead is None:
        raise NotFoundError("Lead", lead_id)

    productos_interes = cambios.pop("productos_interes", None)
    vehiculo = cambios.pop("vehiculo", None)
    for campo, valor in cambios.items():
        setattr(lead, campo, valor)

    ts = _now()
    avisos += _sync_productos_interes(db, lead.id, productos_interes, ts)
    _sync_vehiculos(db, lead.id, vehiculo, ts)

    lead.updated_at = ts
    db.flush()
    db.refresh(lead)
    return _to_response(db, lead), avisos
