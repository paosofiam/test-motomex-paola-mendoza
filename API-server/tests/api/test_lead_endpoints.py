"""Endpoints /leads (capa API, TestClient): POST/GET/GET{id}/PATCH.

Cubre `ciudad` como objeto `{ciudad, estado}` con find-or-create y éxito parcial (estado no
reconocido → lead sin ciudad + header `Warning`), find-or-skip aditivo de `productos_interes`
(multi-match; modelo inexistente → lead sin ese producto + header `Warning`; PATCH aditivo),
find-or-create de `vehiculo`, campos derivados en la respuesta (`estado`, `chat_id`,
`intencion_de_compra` como string Tier 1), validación E.164 y la política `extra="ignore"`.
"""

from sqlalchemy import func, select

from app.models.lead_producto_model import LeadProductoModel
from tests.factories import make_producto


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
    `chat_id`/`status` son derivados: None mientras el lead no tenga chat activo.
    `lead_id` es alias informativo (= id).
    """
    r = client.post("/leads", json=_payload(ciudad={"ciudad": "Guadalajara", "estado": "Jalisco"}))
    assert r.status_code == 201
    body = r.json()
    assert r.headers["location"] == f"/leads/{body['id']}"
    assert body["ciudad"] == "guadalajara"
    assert body["estado"] == "Jalisco"
    assert isinstance(body["intencion_de_compra"], str) and body["intencion_de_compra"]
    assert body["lead_id"] == body["id"]
    assert body["chat_id"] is None
    assert body["status"] is None


def test_post_unknown_estado_is_partial_success(client, seed_catalogs):
    """`ciudad` es find-or-create con éxito parcial: si el estado no se reconoce (ni por nombre ni
    por abreviación), el lead se crea igual SIN ciudad y el aviso viaja en el header `Warning`."""
    r = client.post("/leads", json=_payload(ciudad={"ciudad": "Tijuana", "estado": "Atlantis"}))
    assert r.status_code == 201
    body = r.json()
    assert body["ciudad"] is None
    assert body["estado"] is None
    assert "warning" in {k.lower() for k in r.headers} and "Tijuana" in r.headers["warning"]


def test_post_creates_new_city_under_known_estado(client, seed_catalogs):
    """find-or-create: una ciudad nueva bajo un estado existente (por nombre) se crea y se vincula."""
    r = client.post("/leads", json=_payload(ciudad={"ciudad": "Zapopan", "estado": "Jalisco"}))
    assert r.status_code == 201
    body = r.json()
    assert body["ciudad"] == "zapopan"
    assert body["estado"] == "Jalisco"
    assert "warning" not in {k.lower() for k in r.headers}


def test_post_vehiculo_travels_as_object(client, seed_catalogs):
    r = client.post("/leads", json=_payload(vehiculo=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}]))
    assert r.status_code == 201
    veh = r.json()["vehiculo"]
    assert veh == [{"modelo": "versa", "marca": "nissan", "anio": 2015}]


def test_post_productos_interes_multimatch_persists_all(client, seed_catalogs, db):
    """`productos_interes` es find-or-skip aditivo por modelo: un modelo que matchea dos productos persiste dos filas en leads_productos."""
    make_producto(db, marca="Bosch", modelo="Balata X", precio=100)
    make_producto(db, marca="ATE", modelo="Balata X", precio=200)
    r = client.post("/leads", json=_payload(productos_interes=["Balata X"]))
    assert r.status_code == 201
    lead_id = r.json()["id"]
    n = db.scalar(
        select(func.count()).select_from(LeadProductoModel).where(LeadProductoModel.lead_id == lead_id)
    )
    assert n == 2


def test_post_unknown_producto_interes_skips_with_warning(client, seed_catalogs):
    """`productos_interes` es find-or-skip: un modelo inexistente NO produce 422. El lead se crea
    igual (201) sin ese producto y el modelo omitido se reporta en el header `Warning` (éxito
    parcial, como las ciudades)."""
    r = client.post("/leads", json=_payload(productos_interes=["NoExiste"]))
    assert r.status_code == 201
    assert r.json()["productos_interes"] == []
    assert "warning" in {k.lower() for k in r.headers} and "NoExiste" in r.headers["warning"]


def test_patch_productos_interes_is_additive(client, seed_catalogs, db):
    """En PATCH `productos_interes` es aditivo: combina lo enviado con lo ya vinculado (no reemplaza)."""
    make_producto(db, marca="Bosch", modelo="Filtro A", precio=100)
    make_producto(db, marca="ATE", modelo="Balata B", precio=200)
    created = client.post("/leads", json=_payload(productos_interes=["Filtro A"]))
    lead_id = created.json()["id"]
    r = client.patch(f"/leads/{lead_id}", json={"productos_interes": ["Balata B"]})
    assert r.status_code == 200
    assert sorted(r.json()["productos_interes"]) == ["Balata B", "Filtro A"]


def test_post_rejects_non_e164_phone(client, seed_catalogs):
    assert client.post("/leads", json=_payload(telefono="5512345678")).status_code == 422


def test_post_resolves_estado_by_abbreviation(client, seed_catalogs):
    """El estado de la ciudad se resuelve por abreviación (p. ej. 'JAL' → Jalisco)."""
    r = client.post("/leads", json=_payload(ciudad={"ciudad": "Guadalajara", "estado": "JAL"}))
    assert r.status_code == 201
    assert r.json()["estado"] == "Jalisco"


def test_patch_changes_ciudad(client, seed_catalogs):
    """PATCH cambia la ciudad enviando el objeto `{ciudad, estado}`; el `estado` se re-deriva."""
    lead_id = client.post(
        "/leads", json=_payload(ciudad={"ciudad": "Guadalajara", "estado": "Jalisco"})
    ).json()["id"]
    r = client.patch(f"/leads/{lead_id}", json={"ciudad": {"ciudad": "Zapopan", "estado": "Jalisco"}})
    assert r.status_code == 200
    assert r.json()["ciudad"] == "zapopan"
    assert r.json()["estado"] == "Jalisco"


def test_post_ignores_top_level_estado(client, seed_catalogs):
    """El `estado` de respuesta es derivado de la ciudad: un `estado` suelto a nivel raíz del body
    (fuera del objeto `ciudad`) se descarta (extra="ignore") y no altera el estado derivado."""
    r = client.post("/leads", json=_payload(
        ciudad={"ciudad": "Guadalajara", "estado": "Jalisco"}, estado="Quintana Roo",
    ))
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


def test_get_by_chat_whatsapp_id_returns_single_object(client, seed_catalogs):
    """GET por chat_whatsapp_id devuelve un único objeto (no lista), o 404 si no existe."""
    created = client.post("/leads", json=_payload(chat_whatsapp_id="wa-A")).json()
    client.post("/leads", json=_payload(chat_whatsapp_id="wa-B", telefono="+5213300000000"))
    r = client.get("/leads", params={"chat_whatsapp_id": "wa-A"})
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict)
    assert body["id"] == created["id"] and body["chat_whatsapp_id"] == "wa-A"
    assert client.get("/leads", params={"chat_whatsapp_id": "no-existe"}).status_code == 404


def test_post_is_idempotent_returns_existing_lead(client, seed_catalogs):
    """Idempotente: 2º POST con el mismo chat_whatsapp_id → 200 + el lead existente, sin crear otro."""
    a = client.post("/leads", json=_payload(chat_whatsapp_id="wa-dup", nombre="Uno"))
    b = client.post("/leads", json=_payload(chat_whatsapp_id="wa-dup", nombre="Dos"))
    assert a.status_code == 201
    assert b.status_code == 200
    assert b.headers["location"] == f"/leads/{a.json()['id']}"
    assert b.json()["id"] == a.json()["id"]
    assert b.json()["nombre"] == "Uno"  # body ignorado: devuelve el existente


def test_get_by_id_ok_404_and_chat_id_and_status_derived(client, seed_catalogs):
    """`chat_id` y `status` son derivados del chat activo (join, no columnas): None hasta que existe
    un chat, y reflejan ese chat una vez creado."""
    lead = client.post("/leads", json=_payload()).json()
    sin_chat = client.get(f"/leads/{lead['id']}")
    assert sin_chat.status_code == 200
    assert sin_chat.json()["chat_id"] is None and sin_chat.json()["status"] is None
    assert client.get("/leads/999999").status_code == 404
    chat = client.post("/chats", json={
        "lead_id": lead["id"], "chat_whatsapp_id": lead["chat_whatsapp_id"], "chat_status_id": 1,
    }).json()
    con_chat = client.get(f"/leads/{lead['id']}").json()
    assert con_chat["chat_id"] == chat["id"]
    assert con_chat["status"] == chat["status"]


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
