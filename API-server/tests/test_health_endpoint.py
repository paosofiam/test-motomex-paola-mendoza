"""GET /health: probe de la app y de la BD (capa API, vía TestClient)."""


def test_health_returns_ok_with_db_probe(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("ok", "degraded")
    assert isinstance(body["uptime_seconds"], int)
    assert "timestamp" in body
    # Con el override apuntando a motomex_test, el probe SELECT 1 debe responder ok.
    assert body["db"]["status"] == "ok"
    assert isinstance(body["db"]["latency_ms"], int)
