"""Catálogo monedas (Tier 1): `get_by_id` (activo/soft-deleted) y UNIQUE sobre `abreviacion`.
Poblado por seeder; el modelo es tabla pura (sin create/get_all)."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.mixins import _now
from app.models.moneda_model import MonedaModel


def test_get_by_id_returns_seeded_moneda(db, seed_catalogs):
    mxn = MonedaModel.get_by_id(db, seed_catalogs.moneda_mxn_id)
    assert (mxn.abreviacion, mxn.tipo_de_cambio) == ("MXN", 100)


def test_get_by_id_excludes_soft_deleted(db, seed_catalogs):
    mxn = MonedaModel.get_by_id(db, seed_catalogs.moneda_mxn_id)
    mxn.deleted_at = _now()
    db.flush()
    assert MonedaModel.get_by_id(db, seed_catalogs.moneda_mxn_id) is None


def test_unique_abreviacion(db, seed_catalogs):
    """abreviacion es UNIQUE: una segunda moneda con 'MXN' (ya sembrada) dispara IntegrityError."""
    ts = _now()
    db.add(MonedaModel(moneda="Otro", abreviacion="MXN", tipo_de_cambio=1, created_at=ts, updated_at=ts))
    with pytest.raises(IntegrityError):
        db.flush()
