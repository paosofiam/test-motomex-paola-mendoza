"""DTOs del recurso leads.

`LeadCreate` / `LeadUpdate` reflejan los bodies de `POST` / `PATCH /leads` (`endpoints.md`).
`intencion_de_compra_id` es Tier 1 (id); `ciudad` y `productos_interes` son strings (find-or-fail);
`vehiculo` viaja como lista de objetos (find-or-create con cascada sobre marca). El campo `estado`
NO se acepta en bodies: es derivado de `ciudad → estados`.

`nombre`, `ciudad` y `direccion_envio` son nullable en DB y por tanto opcionales en bodies.

`PATCH` es parcial: todos los campos opcionales y `chat_whatsapp_id` ausente (inmutable tras crear).
`lead_service.update` pasa solo los campos enviados vía `payload.model_dump(exclude_unset=True)` a `LeadModel.update`.

`LeadResponse` incluye los campos derivados `chat_id` (chat activo, None si aún no tiene) y
`estado` (None si `ciudad` es None), además de `intencion_de_compra` ya resuelto a string.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import VehiculoSchema


class LeadCreate(BaseModel):
    chat_whatsapp_id: str
    nombre_whatsapp: str
    telefono: str = Field(..., pattern=r'^\+\d{1,14}$')
    intencion_de_compra_id: int
    nombre: str | None = None
    ciudad: str | None = None
    productos_interes: list[str] = Field(default_factory=list)
    vehiculo: list[VehiculoSchema] = Field(default_factory=list)
    direccion_envio: str | None = None


class LeadUpdate(BaseModel):
    nombre_whatsapp: str | None = None
    telefono: str | None = Field(default=None, pattern=r'^\+\d{1,14}$')
    nombre: str | None = None
    ciudad: str | None = None
    productos_interes: list[str] | None = None
    vehiculo: list[VehiculoSchema] | None = None
    direccion_envio: str | None = None
    intencion_de_compra_id: int | None = None


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int | None = None
    chat_whatsapp_id: str
    nombre_whatsapp: str
    telefono: str
    nombre: str | None = None
    ciudad: str | None = None
    estado: str | None = None
    productos_interes: list[str] = Field(default_factory=list)
    vehiculo: list[VehiculoSchema] = Field(default_factory=list)
    direccion_envio: str | None = None
    intencion_de_compra: str
