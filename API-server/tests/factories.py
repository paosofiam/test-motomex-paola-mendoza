"""Factories mínimas para reducir el setup repetido en los tests de modelos.

Cada helper delega en el `create` del modelo (la matriz), así que respeta las mismas
reglas (find-or-create/fail, columnas estándar, etc.) que el código de producción.
Requieren la fixture `seed_catalogs` cuando dependen de FKs de catálogo (intención, etc.).
"""

from app.models.chat_model import ChatModel
from app.models.lead_model import LeadModel
from app.models.producto_model import ProductoModel


def make_lead(
    db,
    *,
    chat_whatsapp_id="wa-001",
    nombre_whatsapp="Juan",
    telefono="+5213311112222",
    intencion_de_compra_id=1,
    **extra,
):
    return LeadModel.create(
        db,
        chat_whatsapp_id=chat_whatsapp_id,
        nombre_whatsapp=nombre_whatsapp,
        telefono=telefono,
        intencion_de_compra_id=intencion_de_compra_id,
        **extra,
    )


def make_producto(db, *, marca="Nissan", modelo="Versa", precio=12999, moneda_id=1, stock=5, **extra):
    return ProductoModel.create(
        db, marca=marca, modelo=modelo, precio=precio, moneda_id=moneda_id, stock=stock, **extra
    )


def make_chat(db, *, lead_id, chat_whatsapp_id="wa-001", chat_status_id=1, **extra):
    return ChatModel.create(
        db, lead_id=lead_id, chat_whatsapp_id=chat_whatsapp_id, chat_status_id=chat_status_id, **extra
    )
