"""health_service: probe de la app y de la BD (capa service, sin TestClient).

Cubre el camino "ok" (la sesión real responde a `SELECT 1`) y el camino "degraded" forzando un
fallo del probe con un doble cuyo `.execute(...)` lanza (ejercita el `except` de `_check_db`).
"""

from app.schemas.health import HealthResponse
from app.services import health_service


class _BadDB:
    """Doble de `Session` cuyo `.execute` falla: simula la BD caída sin tocar la real."""

    def execute(self, *args, **kwargs):
        raise RuntimeError("db down")


def test_get_health_ok_when_db_responds(db):
    """Con la sesión real el probe responde: status "ok" y timestamp ISO-8601 presente."""
    resp = health_service.get_health(db)
    assert isinstance(resp, HealthResponse)
    assert resp.status == "ok"
    assert resp.db.status == "ok"
    assert isinstance(resp.db.latency_ms, int)
    assert isinstance(resp.uptime_seconds, int)
    assert resp.timestamp


def test_get_health_degraded_when_db_probe_fails():
    """El status global cae a "degraded" si la BD no responde al probe."""
    resp = health_service.get_health(_BadDB())
    assert resp.status == "degraded"
    assert resp.db.status == "error"
    assert resp.db.latency_ms is None
    assert isinstance(resp.uptime_seconds, int)
