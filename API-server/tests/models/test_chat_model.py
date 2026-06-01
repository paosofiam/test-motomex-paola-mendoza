"""ChatModel (Tier 3): un chat activo por lead, lookups más-reciente, update acotado, soft delete."""

from sqlalchemy import select

from app.models.chat_model import ChatModel
from tests.factories import make_chat, make_lead


def test_create_soft_deletes_previous_active(db, seed_catalogs):
    lead = make_lead(db)
    first = make_chat(db, lead_id=lead.id)
    second = make_chat(db, lead_id=lead.id)
    assert first.deleted_at is not None  # el previo quedó soft-deleted
    activos = db.scalars(
        select(ChatModel).where(ChatModel.lead_id == lead.id, ChatModel.deleted_at.is_(None))
    ).all()
    assert len(activos) == 1 and activos[0].id == second.id


def test_get_by_lead_returns_active_most_recent(db, seed_catalogs):
    lead = make_lead(db)
    make_chat(db, lead_id=lead.id)
    second = make_chat(db, lead_id=lead.id)
    assert ChatModel.get_by_lead(db, lead.id).id == second.id


def test_get_by_chat_whatsapp_id(db, seed_catalogs):
    lead = make_lead(db)
    chat = make_chat(db, lead_id=lead.id, chat_whatsapp_id="wa-XYZ")
    assert ChatModel.get_by_chat_whatsapp_id(db, "wa-XYZ").id == chat.id


def test_update_only_touches_status_and_resumen(db, seed_catalogs):
    lead = make_lead(db)
    chat = make_chat(db, lead_id=lead.id)
    updated = ChatModel.update(db, chat.id, chat_status_id=5, resumen="cerrado")
    assert updated.chat_status_id == 5 and updated.resumen == "cerrado"
    assert updated.lead_id == lead.id  # inmutable (no es parámetro de update)


def test_delete_is_soft(db, seed_catalogs):
    lead = make_lead(db)
    chat = make_chat(db, lead_id=lead.id)
    assert ChatModel.delete(db, chat.id) is True
    assert ChatModel.get_by_id(db, chat.id) is None
    assert ChatModel.delete(db, 999999) is False
