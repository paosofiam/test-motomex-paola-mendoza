"""Contrato de errores RFC 7807 transversal (capa API, TestClient).

Verifica que TODA respuesta de error use `application/problem+json` y la forma estándar
(`type/title/status` + `detail`/`instance`), y que la resolución Tier 2 añada `field`/`value_received`,
mientras que `NotFoundError` NO lleva `field`. (`error_handlers.py`.)
"""


def _producto(**over):
    base = dict(
        marca="Nissan", modelo="Versa", precio=12999, moneda_id=1,
        stock=1, especificaciones={}, vehiculos=[], categorias=[], ciudades=[],
    )
    base.update(over)
    return base


def test_not_found_problem_shape(client, seed_catalogs):
    """NotFoundError no expone `field` en el problem+json."""
    r = client.get("/productos/999999")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    body = r.json()
    assert body["status"] == 404
    assert body["title"] == "Not found"
    assert body["type"] == "https://api.example.com/errors/not-found"
    assert body["instance"] == "/productos/999999"
    assert "field" not in body


def test_resolution_error_problem_shape_has_field(client, seed_catalogs):
    """Una resolución que falla (aquí `moneda_id` Tier 1 inexistente) → 422 con `field`/`value_received`."""
    r = client.post("/productos", json=_producto(moneda_id=99999))
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    body = r.json()
    assert body["status"] == 422
    assert body["title"] == "Validation failed"
    assert body["type"] == "https://api.example.com/errors/validation-failed"
    assert body["field"] == "moneda_id"
    assert body["value_received"] == 99999


def test_schema_validation_problem_shape_has_errors(client, seed_catalogs):
    """Una violación de schema (precio<=0) → RequestValidationError de FastAPI → 422 con clave `errors`."""
    r = client.post("/productos", json=_producto(precio=0))
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    body = r.json()
    assert body["title"] == "Validation failed"
    assert "errors" in body
