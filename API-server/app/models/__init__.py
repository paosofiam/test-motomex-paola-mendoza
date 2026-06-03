"""Registro central de modelos ORM.

Importar este paquete registra las 18 tablas en `Base.metadata`, lo que necesitan tanto
la app como Alembic (`env.py` hace `import app.models`) para crear/migrar el esquema y para
resolver las relaciones por nombre de clase. Las importaciones se agrupan en orden por capa:
catálogos Tier 1, catálogos Tier 2, entidades Tier 3 y tablas de relación.
"""

from app.models.moneda_model import MonedaModel
from app.models.estado_model import EstadoModel
from app.models.intencion_de_compra_de_lead_model import IntencionDeCompraDeLeadModel
from app.models.chat_status_model import ChatStatusModel

from app.models.marca_model import MarcaModel
from app.models.categoria_model import CategoriaModel
from app.models.ciudad_model import CiudadModel
from app.models.vehiculo_model import VehiculoModel

from app.models.producto_model import ProductoModel
from app.models.lead_model import LeadModel
from app.models.chat_model import ChatModel
from app.models.pre_orden_model import PreOrdenModel

from app.models.producto_vehiculo_model import ProductoVehiculoModel
from app.models.producto_ciudad_model import ProductoCiudadModel
from app.models.producto_categoria_model import ProductoCategoriaModel
from app.models.lead_producto_model import LeadProductoModel
from app.models.lead_vehiculo_model import LeadVehiculoModel
from app.models.pre_orden_producto_model import PreOrdenProductoModel

__all__ = [
    "MonedaModel",
    "EstadoModel",
    "IntencionDeCompraDeLeadModel",
    "ChatStatusModel",
    "MarcaModel",
    "CategoriaModel",
    "CiudadModel",
    "VehiculoModel",
    "ProductoModel",
    "LeadModel",
    "ChatModel",
    "PreOrdenModel",
    "ProductoVehiculoModel",
    "ProductoCiudadModel",
    "ProductoCategoriaModel",
    "LeadProductoModel",
    "LeadVehiculoModel",
    "PreOrdenProductoModel",
]
