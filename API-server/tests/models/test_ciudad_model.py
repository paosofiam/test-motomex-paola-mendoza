"""CiudadModel (Tier 2): create exige estado_id, normaliza, relación estado; find-or-fail."""

import pytest

from app.core import resolvers
from app.core.exceptions import ResolutionError
from app.models.ciudad_model import CiudadModel


def test_create_normalizes_and_links_estado(db, seed_catalogs):
    """create normaliza el nombre (lowercase/trim/sin acentos) y enlaza el estado por la
    relación lazy="joined", que es la usada para derivar leads.estado."""
    c = CiudadModel.create(db, ciudad="  MONTERREY ", estado_id=seed_catalogs.estado_id)
    assert c.ciudad == "monterrey"
    assert c.estado.estado == "Jalisco"


def test_find_or_create_without_estado_fails_for_new_city(db):
    """Sin estado_id no puede crearse una ciudad nueva, así que el find-or-create degrada
    a find-or-fail efectivo (ResolutionError)."""
    with pytest.raises(ResolutionError) as exc:
        resolvers.find_or_create_ciudad(db, "Tijuana")
    assert exc.value.field == "ciudades"
    assert exc.value.value_received == "Tijuana"


def test_find_or_create_returns_existing(db, seed_catalogs):
    """find-or-create devuelve la ciudad ya sembrada (resuelta por su valor normalizado)
    en vez de crear un duplicado."""
    c = resolvers.find_or_create_ciudad(db, "Guadalajara")
    assert c.id == seed_catalogs.ciudad_id


def test_find_ciudad_or_fail(db, seed_catalogs):
    assert resolvers.find_ciudad_or_fail(db, "Guadalajara").id == seed_catalogs.ciudad_id
    with pytest.raises(ResolutionError) as exc:
        resolvers.find_ciudad_or_fail(db, "Tijuana")
    assert exc.value.field == "ciudad"
