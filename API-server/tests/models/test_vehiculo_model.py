"""VehiculoModel (Tier 2): create normaliza modelo, UNIQUE compuesto, find-or-create cascada."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core import resolvers
from app.models.marca_model import MarcaModel
from app.models.vehiculo_model import VehiculoModel


def test_create_normalizes_modelo(db):
    marca = MarcaModel.create(db, marca="Nissan")
    v = VehiculoModel.create(db, modelo="  VERSA ", marca_id=marca.id, anio=2015)
    assert v.modelo == "versa"
    assert v.created_at == v.updated_at


def test_unique_composite_modelo_marca_anio(db):
    marca = MarcaModel.create(db, marca="Nissan")
    VehiculoModel.create(db, modelo="Versa", marca_id=marca.id, anio=2015)
    with pytest.raises(IntegrityError):
        VehiculoModel.create(db, modelo="versa", marca_id=marca.id, anio=2015)


def test_different_anio_is_distinct(db):
    marca = MarcaModel.create(db, marca="Nissan")
    a = VehiculoModel.create(db, modelo="Versa", marca_id=marca.id, anio=2015)
    b = VehiculoModel.create(db, modelo="Versa", marca_id=marca.id, anio=2016)
    assert a.id != b.id


def test_find_or_create_cascades_marca_and_is_deterministic(db):
    """find-or-create es determinista: la misma tripleta (modelo, marca, anio) normalizada
    devuelve el mismo registro, y la marca se crea en cascada normalizada."""
    a = resolvers.find_or_create_vehiculo(db, "Versa", "Nissan", 2015)
    b = resolvers.find_or_create_vehiculo(db, " versa ", "  NISSÁN ", 2015)
    assert a.id == b.id
    assert a.marca.marca == "nissan"
