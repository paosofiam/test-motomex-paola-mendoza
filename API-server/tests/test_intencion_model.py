"""IntencionDeCompraDeLeadModel (Tier 1): get_all/get_by_id/create + timestamps."""

from app.models.intencion_de_compra_de_lead_model import IntencionDeCompraDeLeadModel


def test_create_and_timestamps(db):
    i = IntencionDeCompraDeLeadModel.create(db, tipo="vip")
    assert i.created_at == i.updated_at
    assert IntencionDeCompraDeLeadModel.get_by_id(db, i.id).tipo == "vip"


def test_get_all_returns_active(db):
    IntencionDeCompraDeLeadModel.create(db, tipo="vip")
    assert len(IntencionDeCompraDeLeadModel.get_all(db)) >= 1
