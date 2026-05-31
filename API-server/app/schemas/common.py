"""Schemas Pydantic compartidos entre recursos (DTOs).

`VehiculoSchema` aplica la convención del contrato: un vehículo SIEMPRE viaja como objeto
`{modelo, marca, anio}` en peticiones y respuestas (nunca un id opaco). `ProblemDetail` modela
RFC 7807 y se usa para documentar las respuestas de error en OpenAPI (`responses=`); el body real
lo construye `app/core/error_handlers.py`.
"""

from pydantic import BaseModel


class VehiculoSchema(BaseModel):
    """Vehículo como objeto `{modelo, marca, anio}` (identidad compuesta del catálogo)."""

    modelo: str
    marca: str
    anio: int


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details (`application/problem+json`).

    `field` y `value_received` son extras opcionales usados en errores de validación/resolución
    (Tier 2 find-or-fail) para que el agente LLM identifique y corrija el valor.
    """

    type: str
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    field: str | None = None
    value_received: str | None = None
