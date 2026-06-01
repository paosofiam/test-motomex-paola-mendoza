"""Capa de orquestación del recurso chats (router → service → model).

Media entre `routers/chats.py` y `ChatModel`: recibe los schemas ya validados por Pydantic, valida
la existencia de los ids referenciados, aplica la regla de un chat activo por lead (el soft-delete
del chat previo lo realiza `ChatModel.create`) y construye el `ChatResponse` que el router devuelve
por HTTP. No conoce FastAPI ni gestiona la transacción (el commit lo hace `get_db`); solo lanza
excepciones de dominio (`NotFoundError`), que `core/error_handlers.py` traduce a RFC 7807.

Construcción de la respuesta (`endpoints.md`): `status` es Tier 1 derivado (string, vía
`chat.chat_status.status`); nunca se devuelve `chat_status_id`.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ResolutionError
from app.models.chat_model import ChatModel
from app.models.chat_status_model import ChatStatusModel
from app.models.lead_model import LeadModel
from app.schemas.chat import ChatCreate, ChatResponse, ChatUpdate


def _to_response(chat: ChatModel) -> ChatResponse:
    """Convierte la instancia ORM al DTO de respuesta, resolviendo el `status` Tier 1 (string)."""
    return ChatResponse(
        id=chat.id,
        lead_id=chat.lead_id,
        chat_whatsapp_id=chat.chat_whatsapp_id,
        status=chat.chat_status.status,
        resumen=chat.resumen,
    )


def create(db: Session, payload: ChatCreate) -> ChatResponse:
    """Crea un chat. `lead_id` (Tier 3) inexistente → `NotFoundError` (→ 404); `chat_status_id`
    (Tier 1, catálogo) que no resuelve → `ResolutionError` (→ 422 con `field`/`value_received`). El
    soft-delete del chat activo previo del mismo lead lo realiza `ChatModel.create` (un chat activo
    por lead).
    """
    if LeadModel.get_by_id(db, payload.lead_id) is None:
        raise NotFoundError("Lead", payload.lead_id)
    if ChatStatusModel.get_by_id(db, payload.chat_status_id) is None:
        raise ResolutionError(field="chat_status_id", value_received=payload.chat_status_id)

    chat = ChatModel.create(db, **payload.model_dump())
    return _to_response(chat)


def get_by_chat_whatsapp_id(db: Session, chat_whatsapp_id: str) -> ChatResponse:
    """Chat activo más reciente por `chat_whatsapp_id`. Lanza `NotFoundError` (→ 404) si no existe."""
    chat = ChatModel.get_by_chat_whatsapp_id(db, chat_whatsapp_id)
    if chat is None:
        raise NotFoundError("Chat", chat_whatsapp_id)
    return _to_response(chat)


def get_by_id(db: Session, chat_id: int) -> ChatResponse:
    """Chat activo por id. Lanza `NotFoundError` (→ 404) si no existe o está soft-deleted."""
    chat = ChatModel.get_by_id(db, chat_id)
    if chat is None:
        raise NotFoundError("Chat", chat_id)
    return _to_response(chat)


def update(db: Session, chat_id: int, payload: ChatUpdate) -> ChatResponse:
    """Actualización parcial (PATCH). Solo `chat_status_id` y `resumen` (lead_id/chat_whatsapp_id
    son inmutables). `exclude_unset=True` pasa solo los campos enviados, alineado con el sentinel
    `_UNSET` de `ChatModel.update`. Si se envía `chat_status_id` no nulo, valida su existencia
    (Tier 1 → `ResolutionError`/422 con `field`/`value_received`) antes de actualizar para evitar un
    fallo de FK en el flush.
    """
    cambios = payload.model_dump(exclude_unset=True)
    nuevo_status_id = cambios.get("chat_status_id")
    if nuevo_status_id is not None and ChatStatusModel.get_by_id(db, nuevo_status_id) is None:
        raise ResolutionError(field="chat_status_id", value_received=nuevo_status_id)

    chat = ChatModel.update(db, chat_id, **cambios)
    if chat is None:
        raise NotFoundError("Chat", chat_id)
    return _to_response(chat)


def delete(db: Session, chat_id: int) -> None:
    """Soft-delete del chat. Lanza `NotFoundError` (→ 404) si no existe o ya está soft-deleted."""
    if not ChatModel.delete(db, chat_id):
        raise NotFoundError("Chat", chat_id)
