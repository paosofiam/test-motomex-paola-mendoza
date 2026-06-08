"""Catálogo intenciones_de_compra_de_leads (Tier 1): `get_by_id`. Poblado por seeder; tabla pura."""

from app.models.intencion_de_compra_de_lead_model import IntencionDeCompraDeLeadModel


def test_get_by_id_returns_seeded_or_none(db, seed_catalogs):
    assert IntencionDeCompraDeLeadModel.get_by_id(db, seed_catalogs.intencion_id).tipo
    assert IntencionDeCompraDeLeadModel.get_by_id(db, 999999) is None
