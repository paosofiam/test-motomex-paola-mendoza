"""Router del recurso chats: frontera HTTP (sin lógica de negocio).

Declara rutas, valida petición/respuesta con Pydantic, fija status HTTP y header `Location`,
y documenta errores RFC 7807. La lógica de negocio vive en `services/chat_service.py`.
"""

from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatCreate, ChatResponse, ChatUpdate
from app.schemas.common import ProblemDetail
from app.services import chat_service

router = APIRouter(prefix="/chats", tags=["chats"])


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
    chat = chat_service.create(db, payload)
    response.headers["Location"] = f"/chats/{chat.id}"
    return chat


@router.get(
    "",
    response_model=ChatResponse,
    responses={404: {"model": ProblemDetail}},
)
def read_chat_by_whatsapp_id(
    chat_whatsapp_id: str, db: Session = Depends(get_db)
) -> Any:
    """Devuelve el chat activo más reciente por `chat_whatsapp_id`. 404 si no existe."""
    return chat_service.get_by_chat_whatsapp_id(db, chat_whatsapp_id)


@router.get(
    "/{chat_id}",
    response_model=ChatResponse,
    responses={404: {"model": ProblemDetail}},
)
def read_chat(chat_id: int, db: Session = Depends(get_db)) -> Any:
    """Devuelve un chat activo por id. 404 si no existe o está soft-deleted."""
    return chat_service.get_by_id(db, chat_id)


@router.patch(
    "/{chat_id}",
    response_model=ChatResponse,
    responses={404: {"model": ProblemDetail}},
)
def update_chat(
    chat_id: int, payload: ChatUpdate, db: Session = Depends(get_db)
) -> Any:
    """Actualización parcial de un chat (solo `chat_status_id` y `resumen`). Devuelve el chat completo."""
    return chat_service.update(db, chat_id, payload)


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ProblemDetail}},
)
def delete_chat(chat_id: int, db: Session = Depends(get_db)) -> None:
    """Soft-delete de un chat. 204 sin body. 404 si no existe o ya está soft-deleted."""
    chat_service.delete(db, chat_id)
