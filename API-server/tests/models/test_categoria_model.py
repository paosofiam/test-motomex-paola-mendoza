"""Catálogo categorias (Tier 2): find-or-create normaliza/idempotente (resolvers), UNIQUE sobre el
valor normalizado, y `get_by_id` en el modelo (tabla pura)."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core import resolvers
from app.core.mixins import _now
from app.models.categoria_model import CategoriaModel


def test_find_or_create_normalizes_value(db):
    c = resolvers.find_or_create_categoria(db, "  BATERÍAS ")
    assert c.categoria == "baterias"
    assert c.created_at == c.updated_at


def test_find_or_create_is_idempotent(db):
    a = resolvers.find_or_create_categoria(db, "Baterías")
    b = resolvers.find_or_create_categoria(db, "  BATERIAS ")
    assert a.id == b.id


def test_unique_on_normalized_value(db):
    """El UNIQUE opera sobre el valor ya normalizado: un duplicado directo dispara IntegrityError."""
    resolvers.find_or_create_categoria(db, "Baterías")
    ts = _now()
    db.add(CategoriaModel(categoria="baterias", created_at=ts, updated_at=ts))
    with pytest.raises(IntegrityError):
        db.flush()


def test_get_by_id_returns_active_or_none(db):
    c = resolvers.find_or_create_categoria(db, "Baterías")
    assert CategoriaModel.get_by_id(db, c.id).id == c.id
    assert CategoriaModel.get_by_id(db, 999999) is None
