"""Seeders de catálogos: Tier 1 con ids/valores EXACTOS (er_diagram.md) + las 32 entidades
federativas (idempotentes por nombre, con abreviación) + idempotencia general."""

from sqlalchemy import func, select

from app.core.mixins import _now
from app.models.chat_status_model import ChatStatusModel
from app.models.estado_model import EstadoModel
from app.models.intencion_de_compra_de_lead_model import IntencionDeCompraDeLeadModel
from app.models.moneda_model import MonedaModel
from seeders import catalog_defaults, estados


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


def test_seed_estados_32_with_abbreviation(db):
    """El seeder puebla las 32 entidades federativas, cada una con su abreviación."""
    estados.seed(db)
    assert db.scalar(select(func.count()).select_from(EstadoModel)) == 32
    nl = db.scalar(select(EstadoModel).where(EstadoModel.estado == "Nuevo León"))
    assert nl.abreviacion == "NL"


def test_seed_estados_idempotent_by_name_and_backfills_abbreviation(db):
    """Idempotente por nombre: una entidad preexistente sin abreviación no se duplica y se le
    rellena la abreviación; el total queda en 32."""
    ts = _now()
    db.add(EstadoModel(estado="Jalisco", created_at=ts, updated_at=ts))
    db.flush()

    estados.seed(db)
    estados.seed(db)

    jaliscos = db.scalar(
        select(func.count()).select_from(EstadoModel).where(EstadoModel.estado == "Jalisco")
    )
    assert jaliscos == 1
    jalisco = db.scalar(select(EstadoModel).where(EstadoModel.estado == "Jalisco"))
    assert jalisco.abreviacion == "JAL"
    assert db.scalar(select(func.count()).select_from(EstadoModel)) == 32
