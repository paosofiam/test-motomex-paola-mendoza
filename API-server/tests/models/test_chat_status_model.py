"""Catálogo chat_statuses (Tier 1): `get_by_id`. Poblado por seeder; tabla pura (sin create/get_all)."""

from app.models.chat_status_model import ChatStatusModel


def test_get_by_id_returns_seeded_or_none(db, seed_catalogs):
    assert ChatStatusModel.get_by_id(db, seed_catalogs.chat_status_id).status == "activo"
    assert ChatStatusModel.get_by_id(db, 999999) is None
