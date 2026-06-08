"""ChatModel (Tier 3): tabla ORM pura. Solo `get_by_id`; el comportamiento (un chat activo por
lead, lookups más-reciente, update acotado, soft delete) vive en `tests/services/test_chat_service.py`.
"""

from tests.factories import make_chat, make_lead


def test_get_by_id_returns_active_or_none(db, seed_catalogs):
    from app.models.chat_model import ChatModel

    lead = make_lead(db)
    chat = make_chat(db, lead_id=lead.id)
    assert ChatModel.get_by_id(db, chat.id).id == chat.id
    assert ChatModel.get_by_id(db, 999999) is None
