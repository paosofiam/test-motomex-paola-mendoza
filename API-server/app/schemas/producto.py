"""DTOs del recurso productos.

`ProductoCreate` refleja el body de `POST /productos` (`endpoints.md`): catálogos Tier 2 como
strings (`marca`, `categorias`, `ciudades`) y vehículos como objetos, todos resueltos en la
capa service (`producto_service.py`). `marca`, `vehiculos` y `categorias` son find-or-create; `ciudades` es
find-or-fail (el payload no lleva estado y la BD exige `estado_id NOT NULL`). `moneda_id`
es Tier 1 (viaja por id, default 1 = MXN).

`ProductoResponse` devuelve `precio` ya convertido a MXN (centavos) y `moneda` como string,
conforme a la regla de conversión de moneda en respuestas.

Dinero siempre como entero en **centavos** (nunca float): en `ProductoCreate`, `precio` va en la
moneda original (`moneda_id`, default 1 = MXN); en `ProductoResponse`, `precio` ya viene en MXN
centavos (lo convierte la capa service). `stock` default 0; `especificaciones` es nullable en DB.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import VehiculoSchema


class ProductoCreate(BaseModel):
    marca: str
    modelo: str
    precio: int = Field(..., gt=0)
    moneda_id: int = 1
    stock: int = Field(0, ge=0)
    especificaciones: dict[str, Any] | None = None
    vehiculos: list[VehiculoSchema] = Field(default_factory=list)
    categorias: list[str] = Field(default_factory=list)
    ciudades: list[str] = Field(default_factory=list)


class ProductoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    marca: str
    modelo: str
    precio: int
    moneda: str
    stock: int
    especificaciones: dict[str, Any] | None = None
