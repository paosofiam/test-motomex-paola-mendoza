"""DTOs del recurso pre_ordenes.

`PreOrdenCreate` exige `producto_id` exacto (Tier 3 — sin resolución por string; el agente
debe consultar `GET /productos` previamente). `total` viaja en MXN centavos ya convertido.
`productos` debe tener al menos un ítem (`min_length=1`).

`PreOrdenProductoResponse` incluye `modelo` (derivado de `productos.modelo`) para que el LLM
pueda razonar sobre la pre-orden sin un GET adicional al producto.
"""

from pydantic import BaseModel, ConfigDict, Field


class PreOrdenProductoCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)


class PreOrdenProductoResponse(BaseModel):
    producto_id: int
    modelo: str
    cantidad: int


class PreOrdenCreate(BaseModel):
    lead_id: int
    total: int = Field(..., gt=0)
    productos: list[PreOrdenProductoCreate] = Field(..., min_length=1)


class PreOrdenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    total: int
    productos: list[PreOrdenProductoResponse]
