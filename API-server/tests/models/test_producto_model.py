"""ProductoModel (Tier 3): create (find-or-create/fail), dinero centavos, search MXN, soft delete."""

import pytest
from sqlalchemy import func, select

from app.core.exceptions import ResolutionError
from app.models.producto_categoria_model import ProductoCategoriaModel
from app.models.producto_model import ProductoModel
from app.models.producto_vehiculo_model import ProductoVehiculoModel


def test_create_finds_or_creates_marca_and_defaults(db, seed_catalogs):
    """La marca se resuelve por find-or-create y se persiste normalizada; la moneda
    cae por defecto a MXN (id 1) y el precio se guarda como int en centavos, nunca float."""
    p = ProductoModel.create(db, marca="Nissan", modelo="Filtro", precio=9999)
    assert p.marca.marca == "nissan"
    assert p.moneda_id == 1
    assert isinstance(p.precio, int)
    assert p.created_at == p.updated_at


def test_create_cascades_vehiculo_and_categoria_relations(db, seed_catalogs):
    """Crear un producto cascada las relaciones con vehículos y categorías; las filas de
    relación nacen con timestamps iguales (created_at == updated_at)."""
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
    assert veh[0].created_at == veh[0].updated_at


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
    """El filtro precio_minimo compara contra el precio convertido a MXN (centavos),
    no contra el precio en la moneda original del producto."""
    ProductoModel.create(db, marca="Bosch", modelo="Bateria", precio=12999, moneda_id=2)
    assert len(ProductoModel.search(db, precio_minimo=220983)) == 1
    assert len(ProductoModel.search(db, precio_minimo=220984)) == 0


def test_delete_is_soft_and_keeps_row(db, seed_catalogs):
    """Soft delete: delete marca deleted_at y get_by_id deja de verla, pero la fila
    permanece físicamente en la BD."""
    p = ProductoModel.create(db, marca="Nissan", modelo="Filtro", precio=9999)
    pid = p.id
    assert ProductoModel.delete(db, pid) is True
    assert ProductoModel.get_by_id(db, pid) is None
    raw = db.get(ProductoModel, pid)
    assert raw is not None and raw.deleted_at is not None
    assert ProductoModel.delete(db, 999999) is False


def test_has_no_update_method():
    assert not hasattr(ProductoModel, "update")
