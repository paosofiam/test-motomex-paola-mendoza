"""Validación pura de los schemas Pydantic (sin DB ni TestClient).

Bloquea regresiones de las reglas declaradas en los schemas de request: formato E.164 del
teléfono, `gt`/`ge` de dinero/cantidad/stock, `min_length` de líneas de pre-orden, defaults
(`moneda_id=1`, `stock=0`, listas vacías) y la política `extra="ignore"` de Pydantic (los campos
no declarados —como `estado`— se descartan, no se rechazan).
"""

import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatCreate, ChatUpdate
from app.schemas.common import VehiculoSchema
from app.schemas.lead import LeadCreate, LeadUpdate
from app.schemas.pre_orden import PreOrdenCreate, PreOrdenProductoCreate
from app.schemas.producto import ProductoCreate


def test_producto_defaults():
    """Defaults del schema: `moneda_id=1` (MXN), `stock=0`, listas vacías y especificaciones None."""
    p = ProductoCreate(marca="Nissan", modelo="Versa", precio=12999)
    assert p.moneda_id == 1
    assert p.stock == 0
    assert p.vehiculos == [] and p.categorias == [] and p.ciudades == []
    assert p.especificaciones is None


def test_producto_precio_must_be_positive():
    with pytest.raises(ValidationError):
        ProductoCreate(marca="Nissan", modelo="Versa", precio=0)
    with pytest.raises(ValidationError):
        ProductoCreate(marca="Nissan", modelo="Versa", precio=-1)


def test_producto_stock_non_negative():
    with pytest.raises(ValidationError):
        ProductoCreate(marca="Nissan", modelo="Versa", precio=1, stock=-1)


def test_producto_ignores_unknown_fields():
    """extra="ignore": un campo no declarado se descarta, no se rechaza."""
    p = ProductoCreate(marca="Nissan", modelo="Versa", precio=1, campo_inventado="x")
    assert not hasattr(p, "campo_inventado")


def _lead_kwargs(**over):
    base = dict(
        chat_whatsapp_id="wa-1",
        nombre_whatsapp="Juan",
        telefono="+5213311112222",
        intencion_de_compra_id=1,
    )
    base.update(over)
    return base


def test_lead_valid_minimal():
    lead = LeadCreate(**_lead_kwargs())
    assert lead.productos_interes == [] and lead.vehiculo == []
    assert lead.nombre is None and lead.ciudad is None


@pytest.mark.parametrize("bad", ["5512345678", "55 1234 5678", "tel", "+", "+123456789012345"])
def test_lead_telefono_must_be_e164(bad):
    with pytest.raises(ValidationError):
        LeadCreate(**_lead_kwargs(telefono=bad))


@pytest.mark.parametrize("good", ["+52", "+5213311112222", "+12345678901234"])
def test_lead_telefono_accepts_valid_e164(good):
    assert LeadCreate(**_lead_kwargs(telefono=good)).telefono == good


def test_lead_requires_mandatory_fields():
    """Omitir un campo obligatorio (aquí `chat_whatsapp_id`) → ValidationError."""
    with pytest.raises(ValidationError):
        LeadCreate(nombre_whatsapp="Juan", telefono="+52", intencion_de_compra_id=1)


def test_lead_ignores_estado_in_body():
    """`estado` es derivado (no se acepta en bodies): extra="ignore" lo descarta sin error."""
    lead = LeadCreate(**_lead_kwargs(estado="Jalisco"))
    assert not hasattr(lead, "estado")


def test_lead_update_all_optional():
    assert LeadUpdate().model_dump(exclude_unset=True) == {}
    u = LeadUpdate(nombre="Real")
    assert u.model_dump(exclude_unset=True) == {"nombre": "Real"}


def test_chat_create_requires_ids():
    """Omitir un id obligatorio (aquí `lead_id`) → ValidationError."""
    with pytest.raises(ValidationError):
        ChatCreate(chat_whatsapp_id="wa-1", chat_status_id=1)


def test_chat_update_only_status_and_resumen():
    """`lead_id` y `chat_whatsapp_id` son inmutables: no son campos de ChatUpdate y extra="ignore" los descarta."""
    u = ChatUpdate(chat_status_id=2, resumen="x", lead_id=99, chat_whatsapp_id="otro")
    assert not hasattr(u, "lead_id") and not hasattr(u, "chat_whatsapp_id")
    assert u.model_dump(exclude_unset=True) == {"chat_status_id": 2, "resumen": "x"}


def test_pre_orden_requires_at_least_one_producto():
    with pytest.raises(ValidationError):
        PreOrdenCreate(lead_id=1, total=100, productos=[])


def test_pre_orden_total_and_cantidad_positive():
    with pytest.raises(ValidationError):
        PreOrdenCreate(lead_id=1, total=0, productos=[PreOrdenProductoCreate(producto_id=1, cantidad=1)])
    with pytest.raises(ValidationError):
        PreOrdenProductoCreate(producto_id=1, cantidad=0)


def test_vehiculo_schema_shape():
    v = VehiculoSchema(modelo="Versa", marca="Nissan", anio=2015)
    assert v.model_dump() == {"modelo": "Versa", "marca": "Nissan", "anio": 2015}


def test_vehiculo_anio_must_be_int():
    with pytest.raises(ValidationError):
        VehiculoSchema(modelo="Versa", marca="Nissan", anio="no-soy-int")
