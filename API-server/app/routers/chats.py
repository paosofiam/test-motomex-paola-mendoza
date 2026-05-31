"""Router del recurso chats: frontera HTTP (sin lógica de negocio).

Declara rutas, valida petición/respuesta con Pydantic, fija status HTTP y header `Location`,
y documenta errores RFC 7807. La lógica vive en la capa service, aún pendiente. Responden 501.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatCreate, ChatResponse, ChatUpdate
from app.schemas.common import ProblemDetail

router = APIRouter(prefix="/chats", tags=["chats"])

_PENDING = "Ruta declarada (stub); pendiente de implementación"


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ProblemDetail}, 422: {"model": ProblemDetail}},
)
def create_chat(
    payload: ChatCreate, response: Response, db: Session = Depends(get_db)
) -> Any:
    """Crea un chat. Soft-delete del chat activo previo obligatorio. Devuelve 201 + Location."""
    # SEAM (pendiente):
    #   chat = chat_service.create(db, payload)
    #   response.headers["Location"] = f"/chats/{chat.id}"
    #   return chat
    # SERVICE: soft-delete del chat activo del lead antes de crear el nuevo (un chat por lead).
    # SERVICE: status=chat.chat_status.status en ChatResponse (Tier 1).
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.get(
    "",
    response_model=ChatResponse,
    responses={404: {"model": ProblemDetail}},
)
def read_chat_by_whatsapp_id(
    chat_whatsapp_id: str | None = None, db: Session = Depends(get_db)
) -> Any:
    """Devuelve el chat más reciente por `chat_whatsapp_id` (ORDER BY created_at DESC LIMIT 1)."""
    # SEAM (pendiente): return chat_service.get_by_chat_whatsapp_id(db, chat_whatsapp_id)
    # SERVICE: status=chat.chat_status.status en ChatResponse (Tier 1).
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.get(
    "/{chat_id}",
    response_model=ChatResponse,
    responses={404: {"model": ProblemDetail}},
)
def read_chat(chat_id: int, db: Session = Depends(get_db)) -> Any:
    """Devuelve un chat activo por id, o 404 si no existe / está soft-deleted."""
    # SEAM (pendiente): return chat_service.get_by_id(db, chat_id)  # NotFoundError -> 404
    # SERVICE: status=chat.chat_status.status en ChatResponse (Tier 1).
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.patch(
    "/{chat_id}",
    response_model=ChatResponse,
    responses={404: {"model": ProblemDetail}},
)
def update_chat(
    chat_id: int, payload: ChatUpdate, db: Session = Depends(get_db)
) -> Any:
    """Actualización parcial de un chat (solo `chat_status_id` y `resumen`). Devuelve el chat completo."""
    # SEAM (pendiente): return chat_service.update(db, chat_id, payload)
    # SERVICE: payload.model_fields_set para distinguir campos enviados de no enviados.
    # SERVICE: status=chat.chat_status.status en ChatResponse (Tier 1).
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ProblemDetail}},
)
def delete_chat(chat_id: int, db: Session = Depends(get_db)) -> None:
    """Soft-delete de un chat. 204 sin body; 404 si no existe / ya está soft-deleted."""
    # SEAM (pendiente): chat_service.delete(db, chat_id)  # NotFoundError -> 404
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)
