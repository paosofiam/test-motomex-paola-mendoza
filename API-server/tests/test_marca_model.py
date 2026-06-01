"""MarcaModel (Tier 2): create normaliza, UNIQUE sobre valor normalizado, find-or-create."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core import resolvers
from app.models.marca_model import MarcaModel


def test_create_normalizes_value(db):
    m = MarcaModel.create(db, marca="  NISSÁN ")
    assert m.marca == "nissan"
    assert m.created_at == m.updated_at


def test_unique_on_normalized_value(db):
    MarcaModel.create(db, marca="Nissan")
    with pytest.raises(IntegrityError):
        MarcaModel.create(db, marca="  nissan ")  # mismo valor normalizado


def test_find_or_create_is_idempotent(db):
    a = resolvers.find_or_create_marca(db, "Nissan")
    b = resolvers.find_or_create_marca(db, "  NISSÁN ")
    assert a.id == b.id  # no duplica
