"""EstadoModel (Tier 1, sin métodos): columnas estándar, UNIQUE, ausencia de métodos."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.mixins import _now
from app.models.estado_model import EstadoModel


def _make(db, nombre):
    ts = _now()
    e = EstadoModel(estado=nombre, created_at=ts, updated_at=ts)
    db.add(e)
    db.flush()
    return e


def test_standard_columns(db):
    e = _make(db, "Nuevo León")
    assert e.created_at == e.updated_at
    assert e.deleted_at is None


def test_unique_estado(db):
    _make(db, "Jalisco")
    with pytest.raises(IntegrityError):
        _make(db, "Jalisco")


def test_has_no_methods():
    for name in ("get_all", "get_by_id", "create", "update", "delete", "search"):
        assert not hasattr(EstadoModel, name), f"EstadoModel no debe exponer {name}"
