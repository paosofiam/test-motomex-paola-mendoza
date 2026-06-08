"""Catálogo ciudades (Tier 2): find-or-create exige estado, normaliza y enlaza el estado;
`find_estado` y `resolver_ciudades` (éxito parcial); `get_by_id` en el modelo (tabla pura)."""

import pytest

from app.core import resolvers
from app.core.exceptions import ResolutionError
from app.models.ciudad_model import CiudadModel


def test_find_or_create_normalizes_and_links_estado(db, seed_catalogs):
    """find-or-create normaliza el nombre (lowercase/trim/sin acentos) y enlaza el estado por la
    relación lazy="joined", usada para derivar leads.estado."""
    c = resolvers.find_or_create_ciudad(db, "  MONTERREY ", seed_catalogs.estado_id)
    assert c.ciudad == "monterrey"
    assert c.estado.estado == "Jalisco"


def test_find_or_create_without_estado_fails_for_new_city(db):
    """Sin estado_id no puede crearse una ciudad nueva, así que el find-or-create degrada a
    find-or-fail efectivo (ResolutionError)."""
    with pytest.raises(ResolutionError) as exc:
        resolvers.find_or_create_ciudad(db, "Tijuana")
    assert exc.value.field == "ciudades"
    assert exc.value.value_received == "Tijuana"


def test_find_or_create_returns_existing(db, seed_catalogs):
    """find-or-create devuelve la ciudad ya sembrada (resuelta por su valor normalizado) en vez de
    crear un duplicado."""
    c = resolvers.find_or_create_ciudad(db, "Guadalajara")
    assert c.id == seed_catalogs.ciudad_id


def test_find_estado_by_name_normalized(db, seed_catalogs):
    """find_estado resuelve por nombre, normalizando acentos/mayúsculas/espacios en ambos lados."""
    assert resolvers.find_estado(db, "  JALISCO ").estado == "Jalisco"
    assert resolvers.find_estado(db, "nuevo leon").estado == "Nuevo León"


def test_find_estado_by_abbreviation(db, seed_catalogs):
    """find_estado también resuelve por la abreviación (p. ej. 'NL', 'CDMX', 'JAL')."""
    assert resolvers.find_estado(db, "JAL").estado == "Jalisco"
    assert resolvers.find_estado(db, "nl").estado == "Nuevo León"
    assert resolvers.find_estado(db, "CDMX").estado == "Ciudad de México"


def test_find_estado_unknown_returns_none(db, seed_catalogs):
    assert resolvers.find_estado(db, "Atlantis") is None


def test_resolver_ciudades_partial_success(db, seed_catalogs):
    """resolver_ciudades vincula las ciudades con estado reconocido y acumula un aviso por cada una
    con estado desconocido (éxito parcial), sin lanzar error."""
    resueltas, avisos = resolvers.resolver_ciudades(db, [
        {"ciudad": "Guadalajara", "estado": "Jalisco"},
        {"ciudad": "Tijuana", "estado": "Atlantis"},
    ])
    assert [c.ciudad for c in resueltas] == ["guadalajara"]
    assert len(avisos) == 1 and "Tijuana" in avisos[0]


def test_get_by_id_returns_active_or_none(db, seed_catalogs):
    assert CiudadModel.get_by_id(db, seed_catalogs.ciudad_id).id == seed_catalogs.ciudad_id
    assert CiudadModel.get_by_id(db, 999999) is None
