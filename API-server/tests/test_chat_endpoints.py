"""Endpoints /chats (capa API, TestClient): POST/GET?/GET{id}/PATCH/DELETE.

Cubre `status` Tier 1 derivado (string), 404 de `lead_id`/`chat_status_id` inexistentes (sin 409),
la regla "un chat activo por lead" (el previo queda soft-deleted), inmutabilidad ignorada en PATCH
y soft delete.
"""

from app.models.chat_model import ChatModel
from tests.factories import make_lead


def _create_lead(client):
    return client.post("/leads", json={
        "chat_whatsapp_id": "wa-chat", "nombre_whatsapp": "Juan",
        "telefono": "+5213311112222", "intencion_de_compra_id": 1,
    }).json()


def _chat_payload(lead, **over):
    base = dict(lead_id=lead["id"], chat_whatsapp_id=lead["chat_whatsapp_id"], chat_status_id=1)
    base.update(over)
    return base


# --- POST -----------------------------------------------------------------------------------

def test_post_creates_with_location_and_status_string(client, seed_catalogs):
    lead = _create_lead(client)
    r = client.post("/chats", json=_chat_payload(lead, resumen="hola"))
    assert r.status_code == 201
    body = r.json()
    assert r.headers["location"] == f"/chats/{body['id']}"
    assert isinstance(body["status"], str) and body["status"]   # Tier 1: string, no chat_status_id
    assert "chat_status_id" not in body
    assert body["lead_id"] == lead["id"]


def test_post_unknown_lead_404(client, seed_catalogs):
    r = client.post("/chats", json={"lead_id": 999999, "chat_whatsapp_id": "x", "chat_status_id": 1})
    assert r.status_code == 404


def test_post_unknown_chat_status_404(client, seed_catalogs):
    # chat_status_id inexistente → 404 (NotFoundError), NO 422.
    lead = _create_lead(client)
    assert client.post("/chats", json=_chat_payload(lead, chat_status_id=999)).status_code == 404


def test_post_enforces_one_active_chat_per_lead(client, seed_catalogs, db):
    lead = _create_lead(client)
    a = client.post("/chats", json=_chat_payload(lead)).json()
    b = client.post("/chats", json=_chat_payload(lead)).json()      # crea B → soft-delete de A
    assert db.get(ChatModel, a["id"]).deleted_at is not None        # A soft-deleted
    assert db.get(ChatModel, b["id"]).deleted_at is None            # B activo
    # GET por chat_whatsapp_id devuelve un único chat (el activo más reciente)
    r = client.get("/chats", params={"chat_whatsapp_id": lead["chat_whatsapp_id"]})
    assert r.status_code == 200
    assert r.json()["id"] == b["id"]


# --- GET ------------------------------------------------------------------------------------

def test_get_by_whatsapp_id_404_when_none(client, seed_catalogs):
    assert client.get("/chats", params={"chat_whatsapp_id": "no-existe"}).status_code == 404


def test_get_by_id_ok_and_404(client, seed_catalogs):
    lead = _create_lead(client)
    cid = client.post("/chats", json=_chat_payload(lead)).json()["id"]
    assert client.get(f"/chats/{cid}").status_code == 200
    assert client.get("/chats/999999").status_code == 404


# --- PATCH ----------------------------------------------------------------------------------

def test_patch_updates_status_and_resumen(client, seed_catalogs):
    lead = _create_lead(client)
    cid = client.post("/chats", json=_chat_payload(lead, chat_status_id=1)).json()["id"]
    r = client.patch(f"/chats/{cid}", json={"chat_status_id": 2, "resumen": "nuevo"})
    assert r.status_code == 200
    assert r.json()["resumen"] == "nuevo"
    assert isinstance(r.json()["status"], str)


def test_patch_unknown_chat_status_404(client, seed_catalogs):
    lead = _create_lead(client)
    cid = client.post("/chats", json=_chat_payload(lead)).json()["id"]
    assert client.patch(f"/chats/{cid}", json={"chat_status_id": 999}).status_code == 404


def test_patch_unknown_chat_404(client, seed_catalogs):
    assert client.patch("/chats/999999", json={"resumen": "x"}).status_code == 404


def test_patch_ignores_immutable_lead_id_and_whatsapp(client, seed_catalogs):
    lead = _create_lead(client)
    chat = client.post("/chats", json=_chat_payload(lead)).json()
    r = client.patch(f"/chats/{chat['id']}", json={
        "resumen": "r", "lead_id": 999999, "chat_whatsapp_id": "otro",
    })
    assert r.status_code == 200
    assert r.json()["lead_id"] == lead["id"]                       # inmutable
    assert r.json()["chat_whatsapp_id"] == lead["chat_whatsapp_id"]  # inmutable


# --- DELETE (soft) --------------------------------------------------------------------------

def test_delete_is_soft_and_idempotent_404(client, seed_catalogs, db):
    lead = _create_lead(client)
    cid = client.post("/chats", json=_chat_payload(lead)).json()["id"]
    assert client.delete(f"/chats/{cid}").status_code == 204
    assert client.get(f"/chats/{cid}").status_code == 404
    assert db.get(ChatModel, cid).deleted_at is not None
    assert client.delete(f"/chats/{cid}").status_code == 404
