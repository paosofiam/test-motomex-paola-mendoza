"""Endpoints /leads (capa API, TestClient): POST/GET/GET{id}/PATCH.

Cubre find-or-fail de `ciudad` y `productos_interes` (multi-match), find-or-create de `vehiculo`,
campos derivados en la respuesta (`estado`, `chat_id`, `intencion_de_compra` como string Tier 1),
validación E.164 y la política `extra="ignore"` para `estado`/`chat_whatsapp_id`.
"""

from sqlalchemy import func, select

from app.models.lead_producto_model import LeadProductoModel
from app.models.producto_model import ProductoModel


def _payload(**over):
    base = dict(
        chat_whatsapp_id="wa-001",
        nombre_whatsapp="Juan",
        telefono="+5213311112222",
        intencion_de_compra_id=1,
    )
    base.update(over)
    return base


def test_post_creates_with_location_and_derived_fields(client, seed_catalogs):
    """`ciudad` es Tier 2 (respuesta normalizada).
    `estado` es derivado: se resuelve por join ciudad → estados, no se almacena.
    `intencion_de_compra` es Tier 1: la respuesta devuelve el string.
    `chat_id` es derivado: None mientras el lead no tenga chat activo.
    """
    r = client.post("/leads", json=_payload(ciudad="Guadalajara"))
    assert r.status_code == 201
    body = r.json()
    assert r.headers["location"] == f"/leads/{body['id']}"
    assert body["ciudad"] == "guadalajara"
    assert body["estado"] == "Jalisco"
    assert isinstance(body["intencion_de_compra"], str) and body["intencion_de_compra"]
    assert body["chat_id"] is None


def test_post_unknown_city_is_find_or_fail(client, seed_catalogs):
    r = client.post("/leads", json=_payload(ciudad="Tijuana"))
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["field"] == "ciudad"
    assert r.json()["value_received"] == "Tijuana"


def test_post_vehiculo_travels_as_object(client, seed_catalogs):
    r = client.post("/leads", json=_payload(vehiculo=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}]))
    assert r.status_code == 201
    veh = r.json()["vehiculo"]
    assert veh == [{"modelo": "versa", "marca": "nissan", "anio": 2015}]


def test_post_productos_interes_multimatch_persists_all(client, seed_catalogs, db):
    """`productos_interes` es find-or-fail por modelo: un modelo que matchea dos productos persiste dos filas en leads_productos."""
    ProductoModel.create(db, marca="Bosch", modelo="Balata X", precio=100)
    ProductoModel.create(db, marca="ATE", modelo="Balata X", precio=200)
    r = client.post("/leads", json=_payload(productos_interes=["Balata X"]))
    assert r.status_code == 201
    lead_id = r.json()["id"]
    n = db.scalar(
        select(func.count()).select_from(LeadProductoModel).where(LeadProductoModel.lead_id == lead_id)
    )
    assert n == 2


def test_post_unknown_producto_interes_fails(client, seed_catalogs):
    r = client.post("/leads", json=_payload(productos_interes=["NoExiste"]))
    assert r.status_code == 422


def test_post_rejects_non_e164_phone(client, seed_catalogs):
    assert client.post("/leads", json=_payload(telefono="5512345678")).status_code == 422


def test_post_ignores_estado_in_body(client, seed_catalogs):
    """`estado` es derivado: extra="ignore" descarta el del body; el estado se sigue derivando de la ciudad."""
    r = client.post("/leads", json=_payload(ciudad="Guadalajara", estado="Quintana Roo"))
    assert r.status_code == 201
    assert r.json()["estado"] == "Jalisco"


def test_post_unknown_intencion_is_422(client, seed_catalogs):
    """`intencion_de_compra_id` es Tier 1 (catálogo): un id que no resuelve → 422 ResolutionError con field/value_received, no un 500 por FK rota."""
    r = client.post("/leads", json=_payload(intencion_de_compra_id=99999))
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    body = r.json()
    assert body["field"] == "intencion_de_compra_id"
    assert body["value_received"] == 99999


def test_patch_unknown_intencion_is_422(client, seed_catalogs):
    lead_id = client.post("/leads", json=_payload()).json()["id"]
    r = client.patch(f"/leads/{lead_id}", json={"intencion_de_compra_id": 99999})
    assert r.status_code == 422
    assert r.json()["field"] == "intencion_de_compra_id"


def test_get_list_filters_by_chat_whatsapp_id(client, seed_catalogs):
    client.post("/leads", json=_payload(chat_whatsapp_id="wa-A"))
    client.post("/leads", json=_payload(chat_whatsapp_id="wa-B", telefono="+5213300000000"))
    res = client.get("/leads", params={"chat_whatsapp_id": "wa-A"}).json()
    assert len(res) == 1 and res[0]["chat_whatsapp_id"] == "wa-A"


def test_get_by_id_ok_404_and_chat_id_derived(client, seed_catalogs):
    """`chat_id` es derivado: al crear un chat activo, aparece en la respuesta del lead (join, no columna)."""
    lead = client.post("/leads", json=_payload()).json()
    assert client.get(f"/leads/{lead['id']}").status_code == 200
    assert client.get("/leads/999999").status_code == 404
    chat = client.post("/chats", json={
        "lead_id": lead["id"], "chat_whatsapp_id": lead["chat_whatsapp_id"], "chat_status_id": 1,
    }).json()
    assert client.get(f"/leads/{lead['id']}").json()["chat_id"] == chat["id"]


def test_patch_partial_updates_and_refreshes_timestamp(client, seed_catalogs, db):
    """update refresca `updated_at` pero deja `created_at` intacto.
    Se fuerzan los timestamps al pasado para esquivar la truncación a segundos de MySQL DATETIME.
    """
    from datetime import datetime
    from app.models.lead_model import LeadModel

    lead_id = client.post("/leads", json=_payload()).json()["id"]
    fila = db.get(LeadModel, lead_id)
    fila.created_at = fila.updated_at = datetime(2020, 1, 1)
    db.flush()

    r = client.patch(f"/leads/{lead_id}", json={"nombre": "Real Name"})
    assert r.status_code == 200 and r.json()["nombre"] == "Real Name"
    db.refresh(fila)
    assert fila.created_at == datetime(2020, 1, 1)
    assert fila.updated_at > fila.created_at


def test_patch_unknown_lead_404(client, seed_catalogs):
    assert client.patch("/leads/999999", json={"nombre": "x"}).status_code == 404


def test_patch_ignores_chat_whatsapp_id(client, seed_catalogs):
    """`chat_whatsapp_id` es inmutable tras crear: el PATCH lo ignora."""
    lead = client.post("/leads", json=_payload(chat_whatsapp_id="wa-immutable")).json()
    r = client.patch(f"/leads/{lead['id']}", json={"chat_whatsapp_id": "wa-changed", "nombre": "N"})
    assert r.status_code == 200
    assert r.json()["chat_whatsapp_id"] == "wa-immutable"
