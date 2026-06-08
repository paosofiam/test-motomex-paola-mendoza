"""Matriz de métodos: cada modelo expone EXACTAMENTE los métodos permitidos (API-server/CLAUDE.md).

Bloquea agregar métodos fuera de contrato y bloquea quitar los permitidos. La constante MATRIX
reproduce la matriz EXACTA de API-server/CLAUDE.md (y contracts.md): las entidades Tier 3
(`productos`, `leads`, `chats`, `pre_ordenes`) son tablas ORM puras y exponen a lo sumo `get_by_id`
(las queries filtradas, create/update/delete con lógica y la orquestación viven en `*_service.py`).
"""

import pytest

from app.models.categoria_model import CategoriaModel
from app.models.chat_model import ChatModel
from app.models.chat_status_model import ChatStatusModel
from app.models.ciudad_model import CiudadModel
from app.models.estado_model import EstadoModel
from app.models.intencion_de_compra_de_lead_model import IntencionDeCompraDeLeadModel
from app.models.lead_model import LeadModel
from app.models.marca_model import MarcaModel
from app.models.moneda_model import MonedaModel
from app.models.pre_orden_model import PreOrdenModel
from app.models.producto_model import ProductoModel
from app.models.vehiculo_model import VehiculoModel


def public_classmethods(cls):
    """Métodos públicos definidos directamente en la clase (classmethod/staticmethod)."""
    return {
        name
        for name, val in vars(cls).items()
        if isinstance(val, (classmethod, staticmethod)) and not name.startswith("_")
    }


MATRIX = {
    MonedaModel: {"get_by_id"},
    EstadoModel: set(),
    ChatStatusModel: {"get_by_id"},
    IntencionDeCompraDeLeadModel: {"get_by_id"},
    MarcaModel: {"get_by_id"},
    CategoriaModel: {"get_by_id"},
    CiudadModel: {"get_by_id"},
    VehiculoModel: {"get_by_id"},
    ProductoModel: {"get_by_id"},
    LeadModel: {"get_by_id"},
    ChatModel: {"get_by_id"},
    PreOrdenModel: set(),
}


@pytest.mark.parametrize(
    "model,expected", list(MATRIX.items()), ids=[m.__name__ for m in MATRIX]
)
def test_model_exposes_exactly_matrix_methods(model, expected):
    assert public_classmethods(model) == expected
