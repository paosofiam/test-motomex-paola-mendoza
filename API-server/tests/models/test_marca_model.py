"""Catálogo marcas (Tier 2): find-or-create normaliza/idempotente (resolvers), UNIQUE sobre el valor
normalizado, y `get_by_id` en el modelo (tabla pura)."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core import resolvers
from app.core.mixins import _now
from app.models.marca_model import MarcaModel


def test_find_or_create_normalizes_value(db):
    m = resolvers.find_or_create_marca(db, "  NISSÁN ")
    assert m.marca == "nissan"
    assert m.created_at == m.updated_at


def test_find_or_create_is_idempotent(db):
    """Dos variantes que normalizan al mismo valor devuelven el mismo registro, sin duplicar."""
    a = resolvers.find_or_create_marca(db, "Nissan")
    b = resolvers.find_or_create_marca(db, "  NISSÁN ")
    assert a.id == b.id


def test_unique_on_normalized_value(db):
    """El UNIQUE opera sobre el valor ya normalizado: un duplicado directo dispara IntegrityError."""
    resolvers.find_or_create_marca(db, "Nissan")
    ts = _now()
    db.add(MarcaModel(marca="nissan", created_at=ts, updated_at=ts))
    with pytest.raises(IntegrityError):
        db.flush()


def test_get_by_id_returns_active_or_none(db):
    m = resolvers.find_or_create_marca(db, "Nissan")
    assert MarcaModel.get_by_id(db, m.id).id == m.id
    assert MarcaModel.get_by_id(db, 999999) is None
