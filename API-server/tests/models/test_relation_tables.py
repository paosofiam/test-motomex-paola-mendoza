"""Tablas de relación N:M: columnas estándar + UNIQUE compuesto (fk1, fk2) + cantidad."""

import pytest
from sqlalchemy import inspect

from app.models.lead_producto_model import LeadProductoModel
from app.models.lead_vehiculo_model import LeadVehiculoModel
from app.models.pre_orden_producto_model import PreOrdenProductoModel
from app.models.producto_categoria_model import ProductoCategoriaModel
from app.models.producto_ciudad_model import ProductoCiudadModel
from app.models.producto_vehiculo_model import ProductoVehiculoModel

RELATION_MODELS = [
    ProductoVehiculoModel,
    ProductoCiudadModel,
    ProductoCategoriaModel,
    LeadProductoModel,
    LeadVehiculoModel,
    PreOrdenProductoModel,
]


@pytest.mark.parametrize("model", RELATION_MODELS, ids=[m.__tablename__ for m in RELATION_MODELS])
def test_standard_columns_present(model):
    cols = inspect(model).columns
    for name in ("id", "created_at", "updated_at", "deleted_at"):
        assert name in cols, f"{model.__tablename__} sin columna {name}"
    assert cols["deleted_at"].nullable is True
    assert cols["created_at"].nullable is False
    assert cols["updated_at"].nullable is False


@pytest.mark.parametrize("model", RELATION_MODELS, ids=[m.__tablename__ for m in RELATION_MODELS])
def test_has_composite_unique_constraint(model):
    uniques = [
        c
        for c in inspect(model).local_table.constraints
        if c.__class__.__name__ == "UniqueConstraint"
    ]
    assert any(len(u.columns) == 2 for u in uniques), (
        f"{model.__tablename__} debe tener UNIQUE compuesto sobre 2 FKs"
    )


def test_pre_orden_producto_has_cantidad():
    cols = inspect(PreOrdenProductoModel).columns
    assert "cantidad" in cols and cols["cantidad"].nullable is False
