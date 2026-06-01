"""Capa de servicio para el health check del servidor.

Verifica conectividad a la BD con una query mínima (`SELECT 1`), calcula el uptime
desde que el proceso arrancó y compone el `HealthResponse`. El estado global es "ok"
solo si todas las dependencias responden; de lo contrario es "degraded".

El `_START_TIME` se fija en el momento en que este módulo se importa por primera vez
(al arrancar el proceso uvicorn), lo que da un uptime fiel al tiempo de vida del worker.
"""

import time
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.health import DBStatus, HealthResponse

_START_TIME = time.monotonic()


def _check_db(db: Session) -> DBStatus:
    try:
        t0 = time.monotonic()
        db.execute(text("SELECT 1"))
        latency_ms = round((time.monotonic() - t0) * 1000)
        return DBStatus(status="ok", latency_ms=latency_ms)
    except Exception:
        return DBStatus(status="error", latency_ms=None)


def get_health(db: Session) -> HealthResponse:
    db_status = _check_db(db)
    overall = "ok" if db_status.status == "ok" else "degraded"
    uptime_seconds = round(time.monotonic() - _START_TIME)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return HealthResponse(
        status=overall,
        timestamp=timestamp,
        uptime_seconds=uptime_seconds,
        db=db_status,
    )
