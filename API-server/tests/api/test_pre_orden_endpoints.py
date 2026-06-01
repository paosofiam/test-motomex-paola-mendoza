"""Endpoint POST /pre_ordenes (capa API, TestClient).

Cubre 201 + Location, `total` en MXN tal cual (sin reconversión), `modelo` derivado por línea,
find-or-fail exacto de `lead_id`/`producto_id` (→ 404, sin resolución por string) y validaciones
de schema (`min_length=1`, `cantidad>0`, `total>0`).
"""


def _setup_lead_and_producto(client):
    lead = client.post("/leads", json={
        "chat_whatsapp_id": "wa-po", "nombre_whatsapp": "Juan",
        "telefono": "+5213311112222", "intencion_de_compra_id": 1,
    }).json()
    prod = client.post("/productos", json={
        "marca": "Nissan", "modelo": "Filtro", "precio": 9999, "moneda_id": 1,
        "stock": 5, "especificaciones": {}, "vehiculos": [], "categorias": [], "ciudades": [],
    }).json()
    return lead, prod


def test_post_creates_with_location_total_and_modelo(client, seed_catalogs):
    lead, prod = _setup_lead_and_producto(client)
    r = client.post("/pre_ordenes", json={
        "lead_id": lead["id"], "total": 29997,
        "productos": [{"producto_id": prod["id"], "cantidad": 3}],
    })
    assert r.status_code == 201
    body = r.json()
    assert r.headers["location"] == f"/pre_ordenes/{body['id']}"
    assert body["total"] == 29997                       # MXN centavos, tal cual
    assert isinstance(body["total"], int)
    linea = body["productos"][0]
    assert linea["producto_id"] == prod["id"]
    assert linea["modelo"] == "Filtro"                  # derivado de producto.modelo
    assert linea["cantidad"] == 3


def test_post_unknown_lead_404(client, seed_catalogs):
    _, prod = _setup_lead_and_producto(client)
    r = client.post("/pre_ordenes", json={
        "lead_id": 999999, "total": 1, "productos": [{"producto_id": prod["id"], "cantidad": 1}],
    })
    assert r.status_code == 404


def test_post_unknown_producto_404(client, seed_catalogs):
    lead, _ = _setup_lead_and_producto(client)
    r = client.post("/pre_ordenes", json={
        "lead_id": lead["id"], "total": 1, "productos": [{"producto_id": 999999, "cantidad": 1}],
    })
    assert r.status_code == 404


def test_post_soft_deleted_producto_404(client, seed_catalogs):
    lead, prod = _setup_lead_and_producto(client)
    client.delete(f"/productos/{prod['id']}")
    r = client.post("/pre_ordenes", json={
        "lead_id": lead["id"], "total": 1, "productos": [{"producto_id": prod["id"], "cantidad": 1}],
    })
    assert r.status_code == 404


def test_post_rejects_empty_productos(client, seed_catalogs):
    lead, _ = _setup_lead_and_producto(client)
    assert client.post("/pre_ordenes", json={"lead_id": lead["id"], "total": 1, "productos": []}).status_code == 422


def test_post_rejects_non_positive_cantidad_and_total(client, seed_catalogs):
    lead, prod = _setup_lead_and_producto(client)
    assert client.post("/pre_ordenes", json={
        "lead_id": lead["id"], "total": 1, "productos": [{"producto_id": prod["id"], "cantidad": 0}],
    }).status_code == 422
    assert client.post("/pre_ordenes", json={
        "lead_id": lead["id"], "total": 0, "productos": [{"producto_id": prod["id"], "cantidad": 1}],
    }).status_code == 422
