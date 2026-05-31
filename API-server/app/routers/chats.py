"""Router stub del recurso chats: rutas declaradas, schemas y lógica pendientes.

Existe para que la superficie de endpoints de `endpoints.md` esté completa. Las cuatro reglas de
negocio relevantes (un chat activo por lead, `created_at DESC LIMIT 1` en las consultas, soft-delete
del chat previo al crear uno nuevo) se implementarán al completar este recurso. Responden 501.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/chats", tags=["chats"])

_PENDING = "Ruta declarada (stub); pendiente de implementación"


@router.post("", status_code=status.HTTP_201_CREATED)
def create_chat():
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.get("")
def read_chat_by_whatsapp_id(chat_whatsapp_id: str | None = None):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.get("/{chat_id}")
def read_chat(chat_id: int):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.patch("/{chat_id}")
def update_chat(chat_id: int):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(chat_id: int):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)
