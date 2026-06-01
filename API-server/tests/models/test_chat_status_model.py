"""ChatStatusModel (Tier 1): get_all/get_by_id; NO create (poblado por seeder)."""

from app.models.chat_status_model import ChatStatusModel


def test_get_all_and_get_by_id(db, seed_catalogs):
    rows = ChatStatusModel.get_all(db)
    assert len(rows) >= 5
    assert ChatStatusModel.get_by_id(db, 1).status == "activo"


def test_has_no_create_method():
    assert not hasattr(ChatStatusModel, "create")
