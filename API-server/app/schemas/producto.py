"""DTOs del recurso productos.

`ProductoCreate` refleja el body de `POST /productos` (`endpoints.md`): catálogos Tier 2 como
strings (`marca`, `categorias`, `ciudades`) y vehículos como objetos, todos resueltos vía
find-or-create en la futura capa service. `moneda_id` es Tier 1 (viaja por id).

`ProductoResponse` devuelve `precio` ya convertido a MXN (centavos) y `moneda` como string,
conforme a la regla de conversión de moneda en respuestas.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import VehiculoSchema


class ProductoCreate(BaseModel):
    marca: str
    modelo: str
    precio: int  # centavos en la moneda original (moneda_id)
    moneda_id: int
    stock: int
    especificaciones: dict[str, Any] = Field(default_factory=dict)
    vehiculos: list[VehiculoSchema] = Field(default_factory=list)
    categorias: list[str] = Field(default_factory=list)
    ciudades: list[str] = Field(default_factory=list)


class ProductoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    marca: str
    modelo: str
    precio: int  # MXN, centavos
    moneda: str
    stock: int
    especificaciones: dict[str, Any] = Field(default_factory=dict)
