"""Seeder de catálogos Tier 1: ids y valores EXACTOS (er_diagram.md) + idempotencia."""

from sqlalchemy import func, select

from app.models.chat_status_model import ChatStatusModel
from app.models.intencion_de_compra_de_lead_model import IntencionDeCompraDeLeadModel
from app.models.moneda_model import MonedaModel
from seeders import catalog_defaults


def test_seed_monedas_exact_values(db):
    catalog_defaults.seed(db)
    mxn, usd, eur = (MonedaModel.get_by_id(db, i) for i in (1, 2, 3))
    assert (mxn.abreviacion, mxn.tipo_de_cambio) == ("MXN", 100)
    assert (usd.abreviacion, usd.tipo_de_cambio) == ("USD", 1700)
    assert (eur.abreviacion, eur.tipo_de_cambio) == ("EUR", 2300)


def test_seed_intenciones_and_statuses(db):
    catalog_defaults.seed(db)
    assert db.scalar(select(func.count()).select_from(IntencionDeCompraDeLeadModel)) == 4
    assert db.scalar(select(func.count()).select_from(ChatStatusModel)) == 5
    assert IntencionDeCompraDeLeadModel.get_by_id(db, 3).tipo == "alta"
    assert ChatStatusModel.get_by_id(db, 5).status == "cerrado"


def test_seed_is_idempotent(db):
    catalog_defaults.seed(db)
    catalog_defaults.seed(db)
    assert db.scalar(select(func.count()).select_from(MonedaModel)) == 3
