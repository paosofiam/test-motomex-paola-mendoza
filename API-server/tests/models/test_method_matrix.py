"""Matriz de métodos: cada modelo expone EXACTAMENTE los métodos permitidos (API-server/CLAUDE.md).

Bloquea agregar métodos fuera de contrato y bloquea quitar los permitidos. La constante MATRIX
reproduce la matriz EXACTA de API-server/CLAUDE.md (y contracts.md); en particular
LeadModel.search respalda GET /leads.
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
    MonedaModel: {"get_all", "get_by_id", "create"},
    EstadoModel: set(),
    ChatStatusModel: {"get_all", "get_by_id"},
    IntencionDeCompraDeLeadModel: {"get_all", "get_by_id", "create"},
    MarcaModel: {"get_all", "get_by_id", "create"},
    CategoriaModel: {"get_all", "get_by_id", "create"},
    CiudadModel: {"get_all", "get_by_id", "create"},
    VehiculoModel: {"get_all", "get_by_id", "create"},
    ProductoModel: {"get_all", "get_by_id", "search", "create", "delete"},
    LeadModel: {"get_by_id", "search", "create", "update"},
    ChatModel: {
        "get_by_id",
        "get_by_chat_whatsapp_id",
        "get_by_lead",
        "create",
        "update",
        "delete",
    },
    PreOrdenModel: {"create"},
}


@pytest.mark.parametrize(
    "model,expected", list(MATRIX.items()), ids=[m.__name__ for m in MATRIX]
)
def test_model_exposes_exactly_matrix_methods(model, expected):
    assert public_classmethods(model) == expected
