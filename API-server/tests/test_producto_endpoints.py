"""Endpoints /productos (capa API, TestClient): CRUD, conversión MXN, Tier 2 (normalización),
find-or-create/find-or-fail, soft delete y ausencia de PATCH (matriz de métodos).

Contrato: tabla de `endpoints.md` (GET/POST/GET{id}/DELETE{id}) e invariantes de `API-server/specs`.
"""

from sqlalchemy import func, select

from app.models.marca_model import MarcaModel
from app.models.producto_model import ProductoModel


def _payload(**over):
    base = dict(
        marca="Nissan", modelo="Versa", precio=12999, moneda_id=1,
        stock=3, especificaciones={"voltaje": "12V"},
        vehiculos=[], categorias=[], ciudades=[],
    )
    base.update(over)
    return base


# --- POST -----------------------------------------------------------------------------------

def test_post_creates_with_location_header(client, seed_catalogs):
    r = client.post("/productos", json=_payload())
    assert r.status_code == 201
    body = r.json()
    assert r.headers["location"] == f"/productos/{body['id']}"
    assert isinstance(body["precio"], int)        # centavos, nunca float
    assert body["moneda"] == "MXN"                 # Tier 1: string, no id
    assert body["marca"] == "nissan"               # Tier 2: normalizado


def test_post_converts_usd_price_to_mxn(client, seed_catalogs):
    # 12999 USD-centavos * tipo_de_cambio 1700 / 100 = 220983 MXN-centavos.
    r = client.post("/productos", json=_payload(marca="Bosch", modelo="Bateria", precio=12999, moneda_id=2))
    assert r.status_code == 201
    body = r.json()
    assert body["precio"] == round(12999 * 1700 / 100) == 220983
    assert body["moneda"] == "USD"


def test_post_converts_eur_price_to_mxn(client, seed_catalogs):
    r = client.post("/productos", json=_payload(marca="ATE", modelo="Disco", precio=10000, moneda_id=3))
    assert r.json()["precio"] == round(10000 * 2300 / 100) == 230000


def test_post_marca_normalizes_and_dedupes(client, seed_catalogs, db):
    client.post("/productos", json=_payload(marca="  NISSÁN ", modelo="A"))
    r2 = client.post("/productos", json=_payload(marca="nissan", modelo="B"))
    assert r2.json()["marca"] == "nissan"
    # find-or-create: ambas resuelven a la MISMA marca, sin duplicar.
    n = db.scalar(select(func.count()).select_from(MarcaModel).where(MarcaModel.marca == "nissan"))
    assert n == 1


def test_post_cascades_vehiculo_and_categoria(client, seed_catalogs, db):
    r = client.post("/productos", json=_payload(
        modelo="ConRel",
        vehiculos=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
        categorias=["Filtros"],
    ))
    assert r.status_code == 201


def test_post_ciudades_is_find_or_fail(client, seed_catalogs):
    # Guadalajara fue sembrada por seed_catalogs → 201.
    assert client.post("/productos", json=_payload(modelo="OK", ciudades=["Guadalajara"])).status_code == 201
    # Ciudad inexistente → 422 problem+json con field/value_received.
    r = client.post("/productos", json=_payload(modelo="Bad", ciudades=["Tijuana"]))
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["field"] == "ciudades"
    assert r.json()["value_received"] == "Tijuana"


def test_post_rejects_non_positive_price(client, seed_catalogs):
    r = client.post("/productos", json=_payload(precio=0))
    assert r.status_code == 422


def test_post_rejects_negative_stock(client, seed_catalogs):
    assert client.post("/productos", json=_payload(stock=-1)).status_code == 422


# --- GET (lista) ----------------------------------------------------------------------------

def test_get_list_filters_by_marca_and_excludes_deleted(client, seed_catalogs, db):
    a = client.post("/productos", json=_payload(marca="Nissan", modelo="Versa")).json()
    client.post("/productos", json=_payload(marca="Toyota", modelo="Corolla"))
    # filtro por marca normalizada
    solo_nissan = client.get("/productos", params={"marca": "  NISSAN "}).json()
    assert all(p["marca"] == "nissan" for p in solo_nissan)
    assert len(solo_nissan) == 1
    # soft-delete excluye de la lista
    client.delete(f"/productos/{a['id']}")
    assert all(p["id"] != a["id"] for p in client.get("/productos").json())


def test_get_list_filters_by_precio_minimo_in_mxn(client, seed_catalogs):
    client.post("/productos", json=_payload(marca="Bosch", modelo="Bateria", precio=12999, moneda_id=2))  # 220983 MXN
    assert len(client.get("/productos", params={"precio_minimo": 220983}).json()) == 1
    assert len(client.get("/productos", params={"precio_minimo": 220984}).json()) == 0


# --- GET /{id} ------------------------------------------------------------------------------

def test_get_by_id_ok_and_404(client, seed_catalogs):
    pid = client.post("/productos", json=_payload()).json()["id"]
    assert client.get(f"/productos/{pid}").status_code == 200
    r = client.get("/productos/999999")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    assert "field" not in r.json()          # NotFoundError no lleva field


# --- DELETE (soft) --------------------------------------------------------------------------

def test_delete_is_soft_and_idempotent_404(client, seed_catalogs, db):
    pid = client.post("/productos", json=_payload()).json()["id"]
    assert client.delete(f"/productos/{pid}").status_code == 204
    assert client.get(f"/productos/{pid}").status_code == 404
    # la fila sigue en BD, solo marcada
    fila = db.get(ProductoModel, pid)
    assert fila is not None and fila.deleted_at is not None
    # segundo delete → 404 (ya soft-deleted)
    assert client.delete(f"/productos/{pid}").status_code == 404


# --- Matriz de métodos ----------------------------------------------------------------------

def test_patch_producto_not_allowed(client, seed_catalogs):
    pid = client.post("/productos", json=_payload()).json()["id"]
    # ProductoModel no tiene update → no hay ruta PATCH.
    assert client.patch(f"/productos/{pid}", json={"stock": 9}).status_code in (404, 405)
