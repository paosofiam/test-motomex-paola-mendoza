"""Excepciones de dominio de la capa de datos.

Los modelos NO conocen FastAPI ni HTTP. Cuando una resolución find-or-fail no encuentra
un registro, lanzan estas excepciones llevando `field` y `value_received`; la futura capa
de controladores las mapeará a respuestas RFC 7807 (`application/problem+json`) con
`422 Unprocessable Entity` (`ResolutionError`) o `404 Not Found` (`NotFoundError`).
"""


class DomainError(Exception):
    """Base para errores de dominio de la capa de datos."""


class ResolutionError(DomainError):
    """Un string Tier 2 (find-or-fail) no resolvió a un registro existente.

    Mapea a 422. `field` y `value_received` alimentan el body RFC 7807.
    """

    def __init__(self, field: str, value_received, detail: str | None = None):
        self.field = field
        self.value_received = value_received
        self.detail = detail or f"El campo '{field}' no se pudo resolver"
        super().__init__(self.detail)


class NotFoundError(DomainError):
    """Una entidad referenciada por id no existe (o está soft-deleted). Mapea a 404."""

    def __init__(self, entity: str, identifier, detail: str | None = None):
        self.entity = entity
        self.identifier = identifier
        self.detail = detail or f"{entity} con id={identifier} no encontrado"
        super().__init__(self.detail)
