"""Columnas estándar en las 18 tablas: id PK, created_at/updated_at NOT NULL, deleted_at NULL."""

import pytest
from sqlalchemy import inspect

import app.models as models

ALL_MODELS = [getattr(models, n) for n in models.__all__]


@pytest.mark.parametrize("model", ALL_MODELS, ids=[m.__name__ for m in ALL_MODELS])
def test_has_standard_columns(model):
    cols = inspect(model).columns
    for name in ("id", "created_at", "updated_at", "deleted_at"):
        assert name in cols, f"{model.__name__} sin columna {name}"
    assert cols["id"].primary_key is True
    assert cols["created_at"].nullable is False
    assert cols["updated_at"].nullable is False
    assert cols["deleted_at"].nullable is True
