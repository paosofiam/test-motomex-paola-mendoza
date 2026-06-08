"""ProductoModel (Tier 3): tabla ORM pura. Solo `get_by_id`; el comportamiento (create con
find-or-create de catálogos, search MXN, soft delete) vive en `tests/services/test_producto_service.py`.
"""

from app.models.producto_model import ProductoModel
from tests.factories import make_producto


def test_get_by_id_returns_active_or_none(db, seed_catalogs):
    producto = make_producto(db)
    assert ProductoModel.get_by_id(db, producto.id).id == producto.id
    assert ProductoModel.get_by_id(db, 999999) is None
