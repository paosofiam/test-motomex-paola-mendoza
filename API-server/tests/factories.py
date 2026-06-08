"""Factories mínimas para reducir el setup repetido en los tests.

Cada helper delega en la CAPA SERVICE (`*_service.create`), que es donde vive ahora la creación
(resolución de catálogos, reconciliación de relaciones, regla de un chat activo por lead). Devuelven
la instancia ORM (vía `get_by_id`) porque los tests consumen atributos del modelo (`.id`,
`.deleted_at`, relaciones). Requieren la fixture `seed_catalogs` cuando dependen de FKs de catálogo.
"""

from app.models.chat_model import ChatModel
from app.models.lead_model import LeadModel
from app.models.producto_model import ProductoModel
from app.schemas.chat import ChatCreate
from app.schemas.lead import LeadCreate
from app.schemas.producto import ProductoCreate
from app.services import chat_service, lead_service, producto_service


def make_lead(
    db,
    *,
    chat_whatsapp_id="wa-001",
    nombre_whatsapp="Juan",
    telefono="+5213311112222",
    intencion_de_compra_id=1,
    **extra,
):
    resp, _ = lead_service.create(
        db,
        LeadCreate(
            chat_whatsapp_id=chat_whatsapp_id,
            nombre_whatsapp=nombre_whatsapp,
            telefono=telefono,
            intencion_de_compra_id=intencion_de_compra_id,
            **extra,
        ),
    )
    return LeadModel.get_by_id(db, resp.id)


def make_producto(db, *, marca="Nissan", modelo="Versa", precio=12999, moneda_id=1, stock=5, **extra):
    resp, _ = producto_service.create(
        db,
        ProductoCreate(marca=marca, modelo=modelo, precio=precio, moneda_id=moneda_id, stock=stock, **extra),
    )
    return ProductoModel.get_by_id(db, resp.id)


def make_chat(db, *, lead_id, chat_whatsapp_id="wa-001", chat_status_id=1, **extra):
    resp = chat_service.create(
        db,
        ChatCreate(lead_id=lead_id, chat_whatsapp_id=chat_whatsapp_id, chat_status_id=chat_status_id, **extra),
    )
    return ChatModel.get_by_id(db, resp.id)
