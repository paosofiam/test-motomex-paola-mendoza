"""PreOrdenModel (Tier 3): solo create; find-or-fail de lead/producto; total MXN tal cual."""

import pytest

from app.core.exceptions import NotFoundError
from app.models.pre_orden_model import PreOrdenModel
from app.models.producto_model import ProductoModel
from tests.factories import make_lead


def test_create_persists_total_and_lines(db, seed_catalogs):
    lead = make_lead(db)
    p = ProductoModel.create(db, marca="Nissan", modelo="Filtro", precio=9999)
    po = PreOrdenModel.create(
        db, lead_id=lead.id, total=29997, productos=[{"producto_id": p.id, "cantidad": 3}]
    )
    assert po.total == 29997                     # MXN centavos, sin recalcular
    assert po.created_at == po.updated_at
    assert len(po.pre_orden_productos) == 1
    assert po.pre_orden_productos[0].cantidad == 3


def test_create_unknown_lead_raises(db, seed_catalogs):
    p = ProductoModel.create(db, marca="Nissan", modelo="Filtro", precio=9999)
    with pytest.raises(NotFoundError):
        PreOrdenModel.create(
            db, lead_id=999999, total=1, productos=[{"producto_id": p.id, "cantidad": 1}]
        )


def test_create_unknown_producto_raises(db, seed_catalogs):
    lead = make_lead(db)
    with pytest.raises(NotFoundError):
        PreOrdenModel.create(
            db, lead_id=lead.id, total=1, productos=[{"producto_id": 999999, "cantidad": 1}]
        )


def test_only_create_method_exists():
    for name in ("get_by_id", "get_all", "update", "delete", "search"):
        assert not hasattr(PreOrdenModel, name)
    assert hasattr(PreOrdenModel, "create")
