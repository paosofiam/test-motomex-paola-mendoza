"""CategoriaModel (Tier 2): create normaliza, UNIQUE normalizado, find-or-create."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core import resolvers
from app.models.categoria_model import CategoriaModel


def test_create_normalizes_value(db):
    c = CategoriaModel.create(db, categoria="  BATERÍAS ")
    assert c.categoria == "baterias"
    assert c.created_at == c.updated_at


def test_unique_on_normalized_value(db):
    CategoriaModel.create(db, categoria="Baterías")
    with pytest.raises(IntegrityError):
        CategoriaModel.create(db, categoria="baterias")


def test_find_or_create_is_idempotent(db):
    a = resolvers.find_or_create_categoria(db, "Baterías")
    b = resolvers.find_or_create_categoria(db, "  BATERIAS ")
    assert a.id == b.id
