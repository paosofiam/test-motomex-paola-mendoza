"""DTOs del recurso health.

`DBStatus` encapsula el resultado del probe de conectividad a la base de datos.
`HealthResponse` es el body completo de `GET /health`: estado global, timestamp UTC,
uptime en segundos y sub-estado de cada dependencia verificada.

El campo `status` del body refleja el estado REAL del servidor:
- "ok"       → todas las dependencias responden correctamente.
- "degraded" → al menos una dependencia falló (e.g. BD inaccesible).
"""

from pydantic import BaseModel


class DBStatus(BaseModel):
    status: str          # "ok" | "error"
    latency_ms: int | None = None


class HealthResponse(BaseModel):
    status: str          # "ok" | "degraded"
    timestamp: str       # ISO 8601 UTC, e.g. "2026-05-31T14:22:10+00:00"
    uptime_seconds: int
    db: DBStatus
