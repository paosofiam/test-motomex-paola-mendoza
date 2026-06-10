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


def test_post_creates_with_location_header(client, seed_catalogs):
    """El precio viaja en centavos (int, nunca float).
    `moneda` es Tier 1: la respuesta devuelve el string, no el id.
    `marca` es Tier 2: la respuesta devuelve el valor normalizado.
    """
    r = client.post("/productos", json=_payload())
    assert r.status_code == 201
    body = r.json()
    assert r.headers["location"] == f"/productos/{body['id']}"
    assert isinstance(body["precio"], int)
    assert body["moneda"] == "MXN"
    assert body["marca"] == "nissan"


def test_post_converts_usd_price_to_mxn(client, seed_catalogs):
    """El precio se convierte a MXN (centavos) vía tipo_de_cambio; ya convertido, la etiqueta `moneda` también es MXN."""
    r = client.post("/productos", json=_payload(marca="Bosch", modelo="Bateria", precio=12999, moneda_id=2))
    assert r.status_code == 201
    body = r.json()
    assert body["precio"] == round(12999 * 1700 / 100) == 220983
    assert body["moneda"] == "MXN"


def test_post_converts_eur_price_to_mxn(client, seed_catalogs):
    r = client.post("/productos", json=_payload(marca="ATE", modelo="Disco", precio=10000, moneda_id=3))
    assert r.json()["precio"] == round(10000 * 2300 / 100) == 230000


def test_post_marca_normalizes_and_dedupes(client, seed_catalogs, db):
    """find-or-create Tier 2: dos variantes (acentos/mayúsculas/espacios) resuelven a la MISMA marca, sin duplicar."""
    client.post("/productos", json=_payload(marca="  NISSÁN ", modelo="A"))
    r2 = client.post("/productos", json=_payload(marca="nissan", modelo="B"))
    assert r2.json()["marca"] == "nissan"
    n = db.scalar(select(func.count()).select_from(MarcaModel).where(MarcaModel.marca == "nissan"))
    assert n == 1


def test_post_cascades_vehiculo_and_categoria(client, seed_catalogs, db):
    r = client.post("/productos", json=_payload(
        modelo="ConRel",
        vehiculos=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
        categorias=["Filtros"],
    ))
    assert r.status_code == 201


def test_post_ciudades_is_find_or_create_with_partial_success(client, seed_catalogs):
    """`ciudades` viaja como `[{ciudad, estado}]` y es find-or-create con éxito parcial: una con
    estado válido se vincula (y aparece en la respuesta); una con estado no reconocido se omite y el
    producto se crea igual con un header `Warning` (no 422)."""
    ok = client.post("/productos", json=_payload(
        modelo="OK", ciudades=[{"ciudad": "Guadalajara", "estado": "Jalisco"}],
    ))
    assert ok.status_code == 201
    assert ok.json()["ciudades"] == [{"ciudad": "guadalajara", "estado": "Jalisco"}]
    assert "warning" not in {k.lower() for k in ok.headers}

    parcial = client.post("/productos", json=_payload(
        modelo="Bad", ciudades=[{"ciudad": "Tijuana", "estado": "Atlantis"}],
    ))
    assert parcial.status_code == 201
    assert parcial.json()["ciudades"] == []
    assert "warning" in {k.lower() for k in parcial.headers}
    assert "Tijuana" in parcial.headers["warning"]


def test_post_response_is_complete_resource(client, seed_catalogs):
    """La respuesta de POST /productos es el recurso completo: además de los campos propios, incluye
    `vehiculos`, `categorias` y `ciudades` ya persistidos (estas como objetos `{ciudad, estado}`)."""
    r = client.post("/productos", json=_payload(
        modelo="Completo",
        vehiculos=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
        categorias=["Baterias"],
        ciudades=[{"ciudad": "Guadalajara", "estado": "JAL"}],
    ))
    assert r.status_code == 201
    body = r.json()
    assert body["vehiculos"] == [{"modelo": "versa", "marca": "nissan", "anio": 2015}]
    assert body["categorias"] == ["baterias"]
    assert body["ciudades"] == [{"ciudad": "guadalajara", "estado": "Jalisco"}]


def test_post_rejects_non_positive_price(client, seed_catalogs):
    r = client.post("/productos", json=_payload(precio=0))
    assert r.status_code == 422


def test_post_rejects_negative_stock(client, seed_catalogs):
    assert client.post("/productos", json=_payload(stock=-1)).status_code == 422


def test_post_unknown_moneda_is_422(client, seed_catalogs):
    """`moneda_id` es Tier 1 (catálogo): un id que no resuelve → 422 ResolutionError con field, no un 500 por FK rota."""
    r = client.post("/productos", json=_payload(moneda_id=99999))
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["field"] == "moneda_id"
    assert r.json()["value_received"] == 99999


def test_get_list_filters_by_marca_and_excludes_deleted(client, seed_catalogs, db):
    """El filtro `marca` normaliza Tier 2 (mayúsculas/espacios) antes de comparar.
    Un producto soft-deleted queda excluido de la lista.
    """
    a = client.post("/productos", json=_payload(marca="Nissan", modelo="Versa")).json()
    client.post("/productos", json=_payload(marca="Toyota", modelo="Corolla"))
    solo_nissan = client.get("/productos", params={"marca": "  NISSAN "}).json()
    assert all(p["marca"] == "nissan" for p in solo_nissan)
    assert len(solo_nissan) == 1
    client.delete(f"/productos/{a['id']}")
    assert all(p["id"] != a["id"] for p in client.get("/productos").json())


def test_get_list_filters_by_precio_minimo_in_mxn(client, seed_catalogs):
    """El filtro `precio_minimo` compara contra el precio ya convertido a MXN (centavos)."""
    client.post("/productos", json=_payload(marca="Bosch", modelo="Bateria", precio=12999, moneda_id=2))
    assert len(client.get("/productos", params={"precio_minimo": 220983}).json()) == 1
    assert len(client.get("/productos", params={"precio_minimo": 220984}).json()) == 0


def test_get_by_id_ok_and_404(client, seed_catalogs):
    """Un id inexistente → 404 NotFoundError, que no lleva `field`."""
    pid = client.post("/productos", json=_payload()).json()["id"]
    assert client.get(f"/productos/{pid}").status_code == 200
    r = client.get("/productos/999999")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    assert "field" not in r.json()


def test_delete_is_soft_and_idempotent_404(client, seed_catalogs, db):
    """El delete es soft: la fila sigue en BD con `deleted_at` marcado.
    Un segundo delete sobre la fila ya soft-deleted → 404.
    """
    pid = client.post("/productos", json=_payload()).json()["id"]
    assert client.delete(f"/productos/{pid}").status_code == 204
    assert client.get(f"/productos/{pid}").status_code == 404
    fila = db.get(ProductoModel, pid)
    assert fila is not None and fila.deleted_at is not None
    assert client.delete(f"/productos/{pid}").status_code == 404


def test_patch_producto_not_allowed(client, seed_catalogs):
    """ProductoModel no tiene update (matriz de métodos): no hay ruta PATCH.
    Si la ruta existe con otros métodos (405), Starlette propaga el header Allow.
    """
    pid = client.post("/productos", json=_payload()).json()["id"]
    r = client.patch(f"/productos/{pid}", json={"stock": 9})
    assert r.status_code in (404, 405)
    if r.status_code == 405:
        assert "GET" in r.headers.get("allow", "")


def test_get_list_filters_by_relations_over_http(client, seed_catalogs):
    """Los filtros de relación viajan como query params y se combinan con AND sobre la colección."""
    versa = client.post("/productos", json=_payload(
        modelo="BateriaVersa",
        vehiculos=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
        categorias=["Baterias"],
    )).json()
    client.post("/productos", json=_payload(modelo="Generico"))
    compat = client.get("/productos", params={"vehiculo_modelo": "versa", "vehiculo_anio": 2015}).json()
    assert [p["id"] for p in compat] == [versa["id"]]
    por_cat = client.get("/productos", params={"categoria": "baterias", "stock_minimo": 1}).json()
    assert [p["id"] for p in por_cat] == [versa["id"]]
    assert client.get("/productos", params={"marca": "inexistente"}).json() == []


def test_get_list_rejects_malformed_query_params(client, seed_catalogs):
    """Valores mal formados → 422 (Pydantic): `order_by` fuera del Literal y `vehiculo_anio` no-entero.
    La cadena vacía SÍ se tolera (ver `test_get_list_empty_optional_params_*`); lo que se rechaza es un
    valor no vacío que no parsea (`abc`)."""
    assert client.get("/productos", params={"order_by": "drop_table"}).status_code == 422
    assert client.get("/productos", params={"vehiculo_anio": "abc"}).status_code == 422


def test_get_list_empty_numeric_param_treated_as_absent(client, seed_catalogs):
    """Robustez para el consumidor LLM: un filtro numérico vacío (`?vehiculo_anio=`) equivale a
    omitirlo (200, no 422). El agente n8n envía el query param aunque el modelo lo deje vacío, y
    marca+modelo sin año es una consulta válida (no debe romper con `int_parsing`)."""
    versa = client.post("/productos", json=_payload(
        modelo="BateriaVersa",
        vehiculos=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
    )).json()
    client.post("/productos", json=_payload(modelo="Generico"))
    r = client.get("/productos", params={
        "vehiculo_marca": "Nissan", "vehiculo_modelo": "Versa", "vehiculo_anio": "",
    })
    assert r.status_code == 200
    assert [p["id"] for p in r.json()] == [versa["id"]]


def test_get_list_empty_params_equal_omitting_them(client, seed_catalogs):
    """`precio_minimo=`/`precio_maximo=` vacíos (numéricos) y `marca=` vacío (string) → 200 y NO
    filtran: el resultado es idéntico a no enviar ningún filtro."""
    client.post("/productos", json=_payload(marca="Nissan", modelo="A"))
    client.post("/productos", json=_payload(marca="Toyota", modelo="B"))
    todos = [p["id"] for p in client.get("/productos").json()]
    vacios = client.get("/productos", params={"precio_minimo": "", "precio_maximo": "", "marca": ""})
    assert vacios.status_code == 200
    assert [p["id"] for p in vacios.json()] == todos
