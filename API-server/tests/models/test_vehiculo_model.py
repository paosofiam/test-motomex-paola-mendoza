"""Catálogo vehiculos (Tier 2): find-or-create normaliza modelo y cascada marca (resolvers), UNIQUE
compuesto (modelo, marca_id, anio), y `get_by_id` en el modelo (tabla pura)."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core import resolvers
from app.core.mixins import _now
from app.models.vehiculo_model import VehiculoModel


def test_find_or_create_normalizes_modelo(db):
    v = resolvers.find_or_create_vehiculo(db, "  VERSA ", "Nissan", 2015)
    assert v.modelo == "versa"
    assert v.created_at == v.updated_at


def test_find_or_create_cascades_marca_and_is_deterministic(db):
    """La misma tripleta (modelo, marca, anio) normalizada devuelve el mismo registro; la marca se
    crea en cascada normalizada."""
    a = resolvers.find_or_create_vehiculo(db, "Versa", "Nissan", 2015)
    b = resolvers.find_or_create_vehiculo(db, " versa ", "  NISSÁN ", 2015)
    assert a.id == b.id
    assert a.marca.marca == "nissan"


def test_different_anio_is_distinct(db):
    a = resolvers.find_or_create_vehiculo(db, "Versa", "Nissan", 2015)
    b = resolvers.find_or_create_vehiculo(db, "Versa", "Nissan", 2016)
    assert a.id != b.id


def test_unique_composite_modelo_marca_anio(db):
    """UNIQUE compuesto (modelo, marca_id, anio): un duplicado directo dispara IntegrityError."""
    v = resolvers.find_or_create_vehiculo(db, "Versa", "Nissan", 2015)
    ts = _now()
    db.add(VehiculoModel(modelo="versa", marca_id=v.marca_id, anio=2015, created_at=ts, updated_at=ts))
    with pytest.raises(IntegrityError):
        db.flush()


def test_get_by_id_returns_active_or_none(db):
    v = resolvers.find_or_create_vehiculo(db, "Versa", "Nissan", 2015)
    assert VehiculoModel.get_by_id(db, v.id).id == v.id
    assert VehiculoModel.get_by_id(db, 999999) is None
