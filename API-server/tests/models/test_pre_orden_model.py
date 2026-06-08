"""PreOrdenModel (Tier 3): tabla ORM pura, sin métodos. La creación (header + líneas) vive en
`pre_orden_service` y se prueba en `tests/services/test_pre_orden_service.py`.
"""

from app.models.pre_orden_model import PreOrdenModel


def test_exposes_no_methods():
    for name in ("get_by_id", "get_all", "update", "delete", "search", "create"):
        assert not hasattr(PreOrdenModel, name)
