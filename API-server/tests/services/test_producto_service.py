"""producto_service: orquestación de /productos (router → service → model).

Invariantes que vive el service (no el modelo): conversión a MXN y armado del DTO
(`precio` int en MXN, `moneda` string), `NotFoundError` (→ 404) en `get_by_id`/`delete`,
y exclusión de soft-deleted en `search`. Se invocan las funciones del módulo directamente
con la `Session` (sin TestClient), igual que el resto de la suite de services.
"""

import pytest

from app.core.exceptions import NotFoundError
from app.models.producto_model import ProductoModel
from app.schemas.producto import ProductoCreate
from app.services import producto_service


def _payload(**over):
    base = dict(marca="Nissan", modelo="Versa", precio=12999, moneda_id=1)
    base.update(over)
    return ProductoCreate(**base)


def test_create_returns_mxn_price_int_and_moneda_string(db, seed_catalogs):
    """Precio MXN (tipo_de_cambio 100) sin cambio, en centavos int (nunca float); `moneda` Tier 1
    como string y `marca` Tier 2 normalizada."""
    resp = producto_service.create(db, _payload(precio=12999, moneda_id=1))
    assert resp.precio == 12999
    assert isinstance(resp.precio, int)
    assert resp.moneda == "MXN"
    assert resp.marca == "nissan"


def test_create_converts_usd_price_to_mxn(db, seed_catalogs):
    """Un precio en USD se convierte a centavos MXN; la etiqueta `moneda` también queda en MXN."""
    resp = producto_service.create(db, _payload(marca="Bosch", modelo="Bateria", precio=12999, moneda_id=2))
    assert resp.precio == round(12999 * 1700 / 100) == 220983
    assert isinstance(resp.precio, int)
    assert resp.moneda == "MXN"


def test_get_by_id_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        producto_service.get_by_id(db, 999999)


def test_get_by_id_returns_active(db, seed_catalogs):
    created = producto_service.create(db, _payload())
    assert producto_service.get_by_id(db, created.id).id == created.id


def test_search_filters_by_marca_and_excludes_soft_deleted(db, seed_catalogs):
    """search normaliza la marca Tier 2 al filtrar y excluye filas soft-deleted (también en get_by_id)."""
    a = producto_service.create(db, _payload(marca="Nissan", modelo="Versa"))
    producto_service.create(db, _payload(marca="Toyota", modelo="Corolla"))
    solo_nissan = producto_service.search(db, marca="  NISSAN ")
    assert [p.id for p in solo_nissan] == [a.id]
    producto_service.delete(db, a.id)
    assert a.id not in [p.id for p in producto_service.search(db)]
    with pytest.raises(NotFoundError):
        producto_service.get_by_id(db, a.id)


def test_delete_unknown_raises_not_found(db, seed_catalogs):
    with pytest.raises(NotFoundError):
        producto_service.delete(db, 999999)


def test_delete_is_soft_keeps_row(db, seed_catalogs):
    """Soft delete: delete devuelve None (204 sin body) y la fila sigue en BD con deleted_at puesto."""
    created = producto_service.create(db, _payload())
    assert producto_service.delete(db, created.id) is None
    raw = db.get(ProductoModel, created.id)
    assert raw is not None and raw.deleted_at is not None
