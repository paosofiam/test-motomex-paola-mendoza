"""chat_service: orquestación de /chats (router → service → model).

Invariantes que vive el service: `lead_id` (Tier 3) inexistente → `NotFoundError` (→ 404);
`chat_status_id` (Tier 1, find-or-fail) que no resuelve → `ResolutionError` (→ 422 con
`field`/`value_received`), validado ANTES del flush en `update` (evita IntegrityError de FK);
`create` IDEMPOTENTE (si ya hay un chat activo con el mismo `lead_id` o `chat_whatsapp_id`, devuelve
el existente sin crear ni borrar; reemplazar exige `delete` previo) y `status` Tier 1 derivado
(string). `create` devuelve `(respuesta, creado)`. Llamadas directas con `Session`.
"""

import pytest

from app.core.exceptions import NotFoundError, ResolutionError
from app.models.chat_model import ChatModel
from app.schemas.chat import ChatCreate, ChatUpdate
from app.services import chat_service
from tests.factories import make_lead


def _create(lead, **over):
    base = dict(lead_id=lead.id, chat_whatsapp_id=lead.chat_whatsapp_id, chat_status_id=1)
    base.update(over)
    return ChatCreate(**base)


def test_create_returns_status_string_not_id(db, seed_catalogs):
    """Tier 1: la respuesta devuelve `status` como string ("activo"), no el `chat_status_id`."""
    lead = make_lead(db)
    resp, creado = chat_service.create(db, _create(lead, resumen="hola"))
    assert creado is True
    assert isinstance(resp.status, str) and resp.status == "activo"
    assert not hasattr(resp, "chat_status_id")
    assert resp.lead_id == lead.id
    assert resp.chat_id == resp.id


def test_create_unknown_lead_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        chat_service.create(db, ChatCreate(lead_id=999999, chat_whatsapp_id="x", chat_status_id=1))


def test_create_unknown_chat_status_raises_resolution_error(db, seed_catalogs):
    """chat_status_id es Tier 1 find-or-fail en el service → ResolutionError (→ 422), NO NotFoundError."""
    lead = make_lead(db)
    with pytest.raises(ResolutionError) as exc:
        chat_service.create(db, _create(lead, chat_status_id=999))
    assert exc.value.field == "chat_status_id"
    assert exc.value.value_received == 999


def test_create_is_idempotent_same_lead(db, seed_catalogs):
    """Idempotente: el segundo create con el mismo lead devuelve el existente (creado=False), sin
    crear uno nuevo ni borrar el anterior."""
    lead = make_lead(db)
    a, creado_a = chat_service.create(db, _create(lead))
    b, creado_b = chat_service.create(db, _create(lead))
    assert creado_a is True and creado_b is False
    assert a.id == b.id
    assert db.get(ChatModel, a.id).deleted_at is None
    assert chat_service.get_by_chat_whatsapp_id(db, lead.chat_whatsapp_id).id == a.id


def test_create_is_idempotent_same_whatsapp_other_lead(db, seed_catalogs):
    """Escenario del fan-out de n8n: aunque cada intento traiga un `lead_id` distinto, comparten
    `chat_whatsapp_id` → el chequeo por (lead_id OR chat_whatsapp_id) devuelve el chat existente y NO
    crea duplicados. (Leads con `chat_whatsapp_id` distinto para que el factory no los colapse; el
    `chat_whatsapp_id` compartido se fija en el body del chat.)"""
    lead_a = make_lead(db, chat_whatsapp_id="wa-a")
    lead_b = make_lead(db, chat_whatsapp_id="wa-b")
    primero, creado1 = chat_service.create(db, _create(lead_a, chat_whatsapp_id="wa-shared"))
    segundo, creado2 = chat_service.create(db, _create(lead_b, chat_whatsapp_id="wa-shared"))
    assert creado1 is True and creado2 is False
    assert primero.id == segundo.id


def test_create_after_delete_creates_new(db, seed_catalogs):
    """Reemplazo vía delete: tras soft-deletear el chat activo, un nuevo create SÍ crea otro
    (la requery de idempotencia trata la fila soft-deleted como inactiva)."""
    lead = make_lead(db)
    a, _ = chat_service.create(db, _create(lead))
    chat_service.delete(db, a.id)
    b, creado = chat_service.create(db, _create(lead))
    assert creado is True
    assert b.id != a.id


def test_get_by_id_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        chat_service.get_by_id(db, 999999)


def test_get_by_chat_whatsapp_id_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        chat_service.get_by_chat_whatsapp_id(db, "no-existe")


def test_update_changes_status_and_resumen(db, seed_catalogs):
    lead = make_lead(db)
    chat, _ = chat_service.create(db, _create(lead, chat_status_id=1))
    updated = chat_service.update(db, chat.id, ChatUpdate(chat_status_id=2, resumen="nuevo"))
    assert updated.resumen == "nuevo"
    assert isinstance(updated.status, str)


def test_update_unknown_chat_status_raises_resolution_error_before_flush(db, seed_catalogs):
    """Valida el chat_status_id (Tier 1) ANTES del flush → ResolutionError, no un IntegrityError de FK."""
    lead = make_lead(db)
    chat, _ = chat_service.create(db, _create(lead))
    with pytest.raises(ResolutionError) as exc:
        chat_service.update(db, chat.id, ChatUpdate(chat_status_id=999))
    assert exc.value.field == "chat_status_id"


def test_update_unknown_chat_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        chat_service.update(db, 999999, ChatUpdate(resumen="x"))


def test_delete_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        chat_service.delete(db, 999999)


def test_delete_is_soft_keeps_row(db, seed_catalogs):
    lead = make_lead(db)
    chat, _ = chat_service.create(db, _create(lead))
    assert chat_service.delete(db, chat.id) is None
    fila = db.get(ChatModel, chat.id)
    assert fila.deleted_at is not None
    assert fila.chat_status_id == chat_service.CHAT_STATUS_CERRADO_ID


def test_delete_closes_chat_overriding_previous_status(db, seed_catalogs):
    """El soft-delete cierra el chat (status → 5) sobrescribiendo cualquier status previo, no solo
    "activo": un chat creado en "con cliente" (4) queda en "cerrado" (5) tras borrarlo."""
    lead = make_lead(db)
    chat, _ = chat_service.create(db, _create(lead, chat_status_id=4))
    chat_service.delete(db, chat.id)
    assert db.get(ChatModel, chat.id).chat_status_id == 5
