"""PreOrdenModel (Tier 3): solo create; total MXN tal cual.

La validación de existencia de `lead_id`/`producto_id` vive en la capa service
(`pre_orden_service`), no en el modelo → se prueba en test_pre_orden_service.py.
"""

from app.models.pre_orden_model import PreOrdenModel
from app.models.producto_model import ProductoModel
from tests.factories import make_lead


def test_create_persists_total_and_lines(db, seed_catalogs):
    """create persiste el total recibido tal cual (MXN en centavos, sin recalcular) junto
    con sus líneas de producto."""
    lead = make_lead(db)
    p = ProductoModel.create(db, marca="Nissan", modelo="Filtro", precio=9999)
    po = PreOrdenModel.create(
        db, lead_id=lead.id, total=29997, productos=[{"producto_id": p.id, "cantidad": 3}]
    )
    assert po.total == 29997
    assert po.created_at == po.updated_at
    assert len(po.pre_orden_productos) == 1
    assert po.pre_orden_productos[0].cantidad == 3


def test_only_create_method_exists():
    for name in ("get_by_id", "get_all", "update", "delete", "search"):
        assert not hasattr(PreOrdenModel, name)
    assert hasattr(PreOrdenModel, "create")
