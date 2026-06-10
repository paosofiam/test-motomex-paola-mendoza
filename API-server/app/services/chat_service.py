"""Capa de orquestación del recurso chats (router → service → model).

Media entre `routers/chats.py` y `ChatModel` (tabla ORM pura): recibe los schemas ya validados por
Pydantic, valida la existencia de los ids referenciados, aplica la regla de un chat activo por
`chat_whatsapp_id` (`create` idempotente: si ya hay uno activo con el mismo `lead_id` o
`chat_whatsapp_id`, devuelve el existente sin crear ni borrar) y construye el `ChatResponse` que el
router devuelve por HTTP.
No conoce FastAPI ni gestiona la transacción (el commit lo hace `get_db`); solo lanza excepciones de
dominio (`NotFoundError`/`ResolutionError`), que `core/error_handlers.py` traduce a RFC 7807.

Construcción de la respuesta (`endpoints.md`): `status` es Tier 1 derivado (string, vía
`chat.chat_status.status`); nunca se devuelve `chat_status_id`. `chat_id` se devuelve además del `id`
como alias informativo (identificador cruzado, simétrico con `Lead`).
"""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ResolutionError
from app.core.mixins import _now
from app.models.chat_model import ChatModel
from app.models.chat_status_model import ChatStatusModel
from app.models.lead_model import LeadModel
from app.schemas.chat import ChatCreate, ChatResponse, ChatUpdate

CHAT_STATUS_CERRADO_ID = 5


def _get_active_by_lead_or_whatsapp(
    db: Session, lead_id: int, chat_whatsapp_id: str
) -> ChatModel | None:
    """Chat activo más reciente con el mismo `lead_id` O el mismo `chat_whatsapp_id`.

    Clave de idempotencia de `create`: en el fan-out del bot varios intentos comparten
    `chat_whatsapp_id` aunque traigan `lead_id` distintos, así que basta con que coincida cualquiera
    de los dos para considerar que ya existe un chat activo. `ORDER BY created_at DESC LIMIT 1`,
    `deleted_at IS NULL`.
    """
    return db.scalar(
        select(ChatModel)
        .where(
            ChatModel.deleted_at.is_(None),
            or_(ChatModel.lead_id == lead_id, ChatModel.chat_whatsapp_id == chat_whatsapp_id),
        )
        .order_by(ChatModel.created_at.desc())
        .limit(1)
    )


def _get_by_chat_whatsapp_id(db: Session, chat_whatsapp_id: str) -> ChatModel | None:
    """Chat activo más reciente por `chat_whatsapp_id` (ORDER BY created_at DESC LIMIT 1)."""
    return db.scalar(
        select(ChatModel)
        .where(ChatModel.chat_whatsapp_id == chat_whatsapp_id, ChatModel.deleted_at.is_(None))
        .order_by(ChatModel.created_at.desc())
        .limit(1)
    )


def _to_response(chat: ChatModel) -> ChatResponse:
    """Convierte la instancia ORM al DTO de respuesta, resolviendo el `status` Tier 1 (string)."""
    return ChatResponse(
        id=chat.id,
        chat_id=chat.id,
        lead_id=chat.lead_id,
        chat_whatsapp_id=chat.chat_whatsapp_id,
        status=chat.chat_status.status,
        resumen=chat.resumen,
    )


def create(db: Session, payload: ChatCreate) -> tuple[ChatResponse, bool]:
    """Crea un chat de forma IDEMPOTENTE. Si ya existe un chat activo con el mismo `lead_id` O el
    mismo `chat_whatsapp_id`, NO crea ni borra: devuelve el existente (el router responde 200). Solo
    si no existe ninguno valida los ids y crea uno nuevo (201).

    `lead_id` (Tier 3) inexistente → `NotFoundError` (→ 404); `chat_status_id` (Tier 1, catálogo) que
    no resuelve → `ResolutionError` (→ 422 con `field`/`value_received`). Un solo chat activo por
    `chat_whatsapp_id`: reemplazar un chat exige `DELETE` previo — `create` NUNCA elimina el anterior.
    `created_at == updated_at`.

    Devuelve `(respuesta, creado)`: `creado=False` cuando se devolvió uno ya existente.
    """
    existente = _get_active_by_lead_or_whatsapp(db, payload.lead_id, payload.chat_whatsapp_id)
    if existente is not None:
        return _to_response(existente), False

    if LeadModel.get_by_id(db, payload.lead_id) is None:
        raise NotFoundError("Lead", payload.lead_id)
    if ChatStatusModel.get_by_id(db, payload.chat_status_id) is None:
        raise ResolutionError(field="chat_status_id", value_received=payload.chat_status_id)

    ts = _now()
    chat = ChatModel(**payload.model_dump(), created_at=ts, updated_at=ts)
    db.add(chat)
    db.flush()
    db.refresh(chat)
    return _to_response(chat), True


def get_by_chat_whatsapp_id(db: Session, chat_whatsapp_id: str) -> ChatResponse:
    """Chat activo más reciente por `chat_whatsapp_id`. Lanza `NotFoundError` (→ 404) si no existe."""
    chat = _get_by_chat_whatsapp_id(db, chat_whatsapp_id)
    if chat is None:
        raise NotFoundError(
            "Chat",
            chat_whatsapp_id,
            detail=f"No existe un chat activo para chat_whatsapp_id={chat_whatsapp_id}",
        )
    return _to_response(chat)


def get_by_id(db: Session, chat_id: int) -> ChatResponse:
    """Chat activo por id. Lanza `NotFoundError` (→ 404) si no existe o está soft-deleted."""
    chat = ChatModel.get_by_id(db, chat_id)
    if chat is None:
        raise NotFoundError("Chat", chat_id)
    return _to_response(chat)


def update(db: Session, chat_id: int, payload: ChatUpdate) -> ChatResponse:
    """Actualización parcial (PATCH). Solo `chat_status_id` y `resumen` (lead_id/chat_whatsapp_id
    son inmutables). `exclude_unset=True` aplica solo los campos enviados. Si se envía
    `chat_status_id` no nulo, valida su existencia (Tier 1 → `ResolutionError`/422) ANTES de mutar y
    flushear, para evitar un fallo de FK en el flush. Refresca `updated_at`. Lanza `NotFoundError`
    (→ 404) si el chat no existe o está soft-deleted.
    """
    cambios = payload.model_dump(exclude_unset=True)
    nuevo_status_id = cambios.get("chat_status_id")
    if nuevo_status_id is not None and ChatStatusModel.get_by_id(db, nuevo_status_id) is None:
        raise ResolutionError(field="chat_status_id", value_received=nuevo_status_id)

    chat = ChatModel.get_by_id(db, chat_id)
    if chat is None:
        raise NotFoundError("Chat", chat_id)
    for campo, valor in cambios.items():
        setattr(chat, campo, valor)

    chat.updated_at = _now()
    db.flush()
    db.refresh(chat)
    return _to_response(chat)


def delete(db: Session, chat_id: int) -> None:
    """Soft-delete del chat: marca `deleted_at` y además lo cierra (`chat_status_id` → 5 cerrado) para
    que la fila borrada quede autoconsistente. En este diseño el `DELETE` de un chat es el único
    mecanismo para terminar/reemplazar la sesión (`endpoints.md` → "Política de borrado"), y terminar
    la sesión es cerrarla; sin esto un chat borrado podría quedar con status "activo", incoherente al
    leer la tabla. `chat_statuses` es Tier 1 sembrado e inmutable, así que el id 5 siempre existe.
    Refresca `updated_at` (se muta una columna de dominio). Lanza `NotFoundError` (→ 404) si no existe
    o ya está soft-deleted.
    """
    chat = ChatModel.get_by_id(db, chat_id)
    if chat is None:
        raise NotFoundError("Chat", chat_id)
    ts = _now()
    chat.chat_status_id = CHAT_STATUS_CERRADO_ID
    chat.deleted_at = ts
    chat.updated_at = ts
