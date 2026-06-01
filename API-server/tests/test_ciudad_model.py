"""CiudadModel (Tier 2): create exige estado_id, normaliza, relación estado; find-or-fail."""

import pytest

from app.core import resolvers
from app.core.exceptions import ResolutionError
from app.models.ciudad_model import CiudadModel


def test_create_normalizes_and_links_estado(db, seed_catalogs):
    c = CiudadModel.create(db, ciudad="  MONTERREY ", estado_id=seed_catalogs.estado_id)
    assert c.ciudad == "monterrey"
    assert c.estado.estado == "Jalisco"  # relación lazy="joined" para derivar leads.estado


def test_find_or_create_without_estado_fails_for_new_city(db):
    # Sin estado_id no se puede crear una ciudad nueva → find-or-fail efectivo.
    with pytest.raises(ResolutionError) as exc:
        resolvers.find_or_create_ciudad(db, "Tijuana")
    assert exc.value.field == "ciudades"
    assert exc.value.value_received == "Tijuana"


def test_find_or_create_returns_existing(db, seed_catalogs):
    c = resolvers.find_or_create_ciudad(db, "Guadalajara")  # ya sembrada (normalizada)
    assert c.id == seed_catalogs.ciudad_id


def test_find_ciudad_or_fail(db, seed_catalogs):
    assert resolvers.find_ciudad_or_fail(db, "Guadalajara").id == seed_catalogs.ciudad_id
    with pytest.raises(ResolutionError) as exc:
        resolvers.find_ciudad_or_fail(db, "Tijuana")
    assert exc.value.field == "ciudad"
