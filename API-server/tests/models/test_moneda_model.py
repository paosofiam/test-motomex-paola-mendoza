"""MonedaModel (Tier 1): get_all/get_by_id/create, timestamps, soft-delete, UNIQUE."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.mixins import _now
from app.models.moneda_model import MonedaModel


def test_create_sets_equal_timestamps(db):
    m = MonedaModel.create(db, moneda="Libra", abreviacion="GBP", tipo_de_cambio=2500)
    assert m.id is not None
    assert m.created_at == m.updated_at
    assert m.deleted_at is None


def test_create_keeps_value_unnormalized(db):
    """Tier 1: el string se persiste y devuelve tal cual, sin lowercase ni quitar acentos."""
    m = MonedaModel.create(db, moneda="Pesos", abreviacion="MXN", tipo_de_cambio=100)
    assert m.abreviacion == "MXN"


def test_get_by_id_returns_active(db):
    m = MonedaModel.create(db, moneda="Libra", abreviacion="GBP", tipo_de_cambio=2500)
    assert MonedaModel.get_by_id(db, m.id) is m


def test_get_all_excludes_soft_deleted(db):
    m = MonedaModel.create(db, moneda="Libra", abreviacion="GBP", tipo_de_cambio=2500)
    m.deleted_at = _now()
    db.flush()
    assert MonedaModel.get_by_id(db, m.id) is None
    assert m.id not in [r.id for r in MonedaModel.get_all(db)]


def test_unique_abreviacion(db):
    MonedaModel.create(db, moneda="Dólar", abreviacion="USD", tipo_de_cambio=1700)
    with pytest.raises(IntegrityError):
        MonedaModel.create(db, moneda="Otro", abreviacion="USD", tipo_de_cambio=1)
