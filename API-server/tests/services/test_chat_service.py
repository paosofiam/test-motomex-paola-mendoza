"""chat_service: orquestación de /chats (router → service → model).

Invariantes que vive el service: validación de `lead_id`/`chat_status_id` → `NotFoundError`
(→ 404, NO 422), regla "un chat activo por lead" (el soft-delete del previo lo hace el modelo),
validación de `chat_status_id` ANTES del flush en `update` (evita IntegrityError de FK) y `status`
Tier 1 derivado (string). Llamadas directas con `Session`.
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
    lead = make_lead(db)
    resp = chat_service.create(db, _create(lead, resumen="hola"))
    assert isinstance(resp.status, str) and resp.status == "activo"  # Tier 1: string
    assert not hasattr(resp, "chat_status_id")
    assert resp.lead_id == lead.id


def test_create_unknown_lead_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        chat_service.create(db, ChatCreate(lead_id=999999, chat_whatsapp_id="x", chat_status_id=1))


def test_create_unknown_chat_status_raises_resolution_error(db, seed_catalogs):
    # chat_status_id es Tier 1 find-or-fail en el service → ResolutionError (→ 422), NO NotFoundError.
    lead = make_lead(db)
    with pytest.raises(ResolutionError) as exc:
        chat_service.create(db, _create(lead, chat_status_id=999))
    assert exc.value.field == "chat_status_id"
    assert exc.value.value_received == 999


def test_create_enforces_one_active_chat_per_lead(db, seed_catalogs):
    lead = make_lead(db)
    a = chat_service.create(db, _create(lead))
    b = chat_service.create(db, _create(lead))      # crea B → soft-delete de A
    assert db.get(ChatModel, a.id).deleted_at is not None
    assert db.get(ChatModel, b.id).deleted_at is None
    # lookup devuelve el activo más reciente
    assert chat_service.get_by_chat_whatsapp_id(db, lead.chat_whatsapp_id).id == b.id


def test_get_by_id_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        chat_service.get_by_id(db, 999999)


def test_get_by_chat_whatsapp_id_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        chat_service.get_by_chat_whatsapp_id(db, "no-existe")


def test_update_changes_status_and_resumen(db, seed_catalogs):
    lead = make_lead(db)
    chat = chat_service.create(db, _create(lead, chat_status_id=1))
    updated = chat_service.update(db, chat.id, ChatUpdate(chat_status_id=2, resumen="nuevo"))
    assert updated.resumen == "nuevo"
    assert isinstance(updated.status, str)


def test_update_unknown_chat_status_raises_resolution_error_before_flush(db, seed_catalogs):
    # Valida el chat_status_id (Tier 1) ANTES de actualizar → ResolutionError, no un IntegrityError de FK.
    lead = make_lead(db)
    chat = chat_service.create(db, _create(lead))
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
    chat = chat_service.create(db, _create(lead))
    assert chat_service.delete(db, chat.id) is None
    assert db.get(ChatModel, chat.id).deleted_at is not None
