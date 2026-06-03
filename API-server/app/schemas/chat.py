"""DTOs del recurso chats.

`ChatCreate` refleja el body de `POST /chats`. `lead_id` y `chat_whatsapp_id` son inmutables
tras crear — no aparecen en `ChatUpdate` (CLAUDE.md invariante). `chat_status_id` es Tier 1
(id en body → string en respuesta).

`ChatUpdate` es parcial: la service layer usa `payload.model_fields_set` para distinguir
campos enviados de no enviados.

`ChatResponse` devuelve `status` ya resuelto a string (Tier 1: derivado del join con
`chat_statuses`).
"""

from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    lead_id: int
    chat_whatsapp_id: str
    chat_status_id: int
    resumen: str | None = None


class ChatUpdate(BaseModel):
    chat_status_id: int | None = None
    resumen: str | None = None


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    chat_whatsapp_id: str
    status: str
    resumen: str | None = None
