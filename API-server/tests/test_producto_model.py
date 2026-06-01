"""ProductoModel (Tier 3): create (find-or-create/fail), dinero centavos, search MXN, soft delete."""

import pytest
from sqlalchemy import func, select

from app.core.exceptions import ResolutionError
from app.models.producto_categoria_model import ProductoCategoriaModel
from app.models.producto_model import ProductoModel
from app.models.producto_vehiculo_model import ProductoVehiculoModel


def test_create_finds_or_creates_marca_and_defaults(db, seed_catalogs):
    p = ProductoModel.create(db, marca="Nissan", modelo="Filtro", precio=9999)
    assert p.marca.marca == "nissan"          # find-or-create normalizado
    assert p.moneda_id == 1                    # default MXN
    assert isinstance(p.precio, int)           # centavos, nunca float
    assert p.created_at == p.updated_at


def test_create_cascades_vehiculo_and_categoria_relations(db, seed_catalogs):
    p = ProductoModel.create(
        db,
        marca="Nissan",
        modelo="Filtro",
        precio=9999,
        vehiculos=[{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
        categorias=["Filtros"],
    )
    veh = db.scalars(
        select(ProductoVehiculoModel).where(ProductoVehiculoModel.producto_id == p.id)
    ).all()
    cat = db.scalars(
        select(ProductoCategoriaModel).where(ProductoCategoriaModel.producto_id == p.id)
    ).all()
    assert len(veh) == 1 and len(cat) == 1
    assert veh[0].created_at == veh[0].updated_at  # relación con timestamps iguales


def test_create_ciudad_is_find_or_fail(db, seed_catalogs):
    ok = ProductoModel.create(db, marca="Nissan", modelo="X", precio=1, ciudades=["Guadalajara"])
    assert ok.id is not None
    with pytest.raises(ResolutionError):
        ProductoModel.create(db, marca="Nissan", modelo="Y", precio=1, ciudades=["Tijuana"])


def test_search_by_marca_uses_normalization(db, seed_catalogs):
    ProductoModel.create(db, marca="Nissan", modelo="Filtro", precio=9999)
    assert len(ProductoModel.search(db, marca="  NISSÁN ")) == 1
    assert len(ProductoModel.search(db, marca="Toyota")) == 0


def test_search_precio_minimo_converts_to_mxn(db, seed_catalogs):
    # 129.99 USD * 17.00 = 220983 centavos MXN (round(12999 * 1700 / 100)).
    ProductoModel.create(db, marca="Bosch", modelo="Bateria", precio=12999, moneda_id=2)
    assert len(ProductoModel.search(db, precio_minimo=220983)) == 1
    assert len(ProductoModel.search(db, precio_minimo=220984)) == 0


def test_delete_is_soft_and_keeps_row(db, seed_catalogs):
    p = ProductoModel.create(db, marca="Nissan", modelo="Filtro", precio=9999)
    pid = p.id
    assert ProductoModel.delete(db, pid) is True
    assert ProductoModel.get_by_id(db, pid) is None         # excluido por deleted_at
    raw = db.get(ProductoModel, pid)
    assert raw is not None and raw.deleted_at is not None    # la fila sigue en BD
    assert ProductoModel.delete(db, 999999) is False


def test_has_no_update_method():
    assert not hasattr(ProductoModel, "update")
