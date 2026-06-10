"""DTOs del recurso leads.

`LeadCreate` / `LeadUpdate` reflejan los bodies de `POST` / `PATCH /leads` (`endpoints.md`).
`intencion_de_compra_id` es Tier 1 (id); `productos_interes` son strings (modelos) con find-or-skip
aditivo: un modelo que no exista en inventario no falla, se omite y el aviso va en el header
`Warning` (el lead se crea/edita igual). `vehiculo` viaja como lista de objetos (find-or-create con
cascada sobre marca). `ciudad` viaja como objeto `{ciudad, estado}`: el estado da contexto para
resolver/crear la ciudad y se resuelve con éxito parcial (si el estado no existe, el lead se guarda
sin ciudad y el aviso va en el header `Warning`). En la respuesta, `estado` se sigue derivando de
`ciudad → estados`.

`nombre`, `ciudad` y `direccion_envio` son nullable en DB y por tanto opcionales en bodies.

`PATCH` es parcial: todos los campos opcionales y `chat_whatsapp_id` ausente (inmutable tras crear).
`lead_service.update` aplica solo los campos enviados vía `payload.model_dump(exclude_unset=True)`. Las
relaciones `productos_interes` y `vehiculo` se vinculan de forma aditiva (combinan con lo existente,
nunca reemplazan ni borran; lista vacía u omitida = sin cambios, no hay remoción vía API).

`LeadResponse` incluye los campos derivados `chat_id` y `status` (del chat activo, None si aún no
tiene) y `estado` (None si `ciudad` es None), además de `intencion_de_compra` ya resuelto a string.
Devuelve también un alias `lead_id` (= `id`): identificador cruzado informativo, simétrico con
`ChatResponse`, para que el consumidor LLM tenga lead/chat ids consulte el recurso que consulte.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import CiudadEstadoSchema, VehiculoSchema


class LeadCreate(BaseModel):
    chat_whatsapp_id: str
    nombre_whatsapp: str
    telefono: str = Field(..., pattern=r'^\+\d{1,14}$')
    intencion_de_compra_id: int
    nombre: str | None = None
    ciudad: CiudadEstadoSchema | None = None
    productos_interes: list[str] = Field(default_factory=list)
    vehiculo: list[VehiculoSchema] = Field(default_factory=list)
    direccion_envio: str | None = None


class LeadUpdate(BaseModel):
    nombre_whatsapp: str | None = None
    telefono: str | None = Field(default=None, pattern=r'^\+\d{1,14}$')
    nombre: str | None = None
    ciudad: CiudadEstadoSchema | None = None
    productos_interes: list[str] | None = None
    vehiculo: list[VehiculoSchema] | None = None
    direccion_envio: str | None = None
    intencion_de_compra_id: int | None = None


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    chat_id: int | None = None
    status: str | None = None
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
