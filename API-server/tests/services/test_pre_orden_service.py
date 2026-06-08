"""pre_orden_service: find-or-fail Tier 3 (lead_id/producto_id exactos) → NotFoundError.

La validación de existencia se movió del modelo al service; aquí se cubre ese invariante
(la skill exige que `producto_id`/`lead_id` inexistentes → 404, sin resolución por string).
"""

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.pre_orden import PreOrdenCreate, PreOrdenProductoCreate
from app.services import pre_orden_service
from tests.factories import make_lead, make_producto


def _payload(lead_id, producto_id, *, total=1, cantidad=1):
    return PreOrdenCreate(
        lead_id=lead_id,
        total=total,
        productos=[PreOrdenProductoCreate(producto_id=producto_id, cantidad=cantidad)],
    )


def test_create_unknown_lead_raises_not_found(db, seed_catalogs):
    p = make_producto(db, marca="Nissan", modelo="Filtro", precio=9999)
    with pytest.raises(NotFoundError):
        pre_orden_service.create(db, _payload(999999, p.id))


def test_create_unknown_producto_raises_not_found(db, seed_catalogs):
    lead = make_lead(db)
    with pytest.raises(NotFoundError):
        pre_orden_service.create(db, _payload(lead.id, 999999))


def test_create_valid_returns_response_with_total_and_modelo(db, seed_catalogs):
    """`total` se devuelve tal cual en centavos MXN y `modelo` es derivado de producto.modelo."""
    lead = make_lead(db)
    p = make_producto(db, marca="Nissan", modelo="Filtro", precio=9999)
    resp = pre_orden_service.create(db, _payload(lead.id, p.id, total=29997, cantidad=3))
    assert resp.total == 29997
    assert resp.productos[0].modelo == "Filtro"
    assert resp.productos[0].cantidad == 3
