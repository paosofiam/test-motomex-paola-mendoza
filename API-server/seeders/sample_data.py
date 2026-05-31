"""Datos de ejemplo MÍNIMOS y deterministas (sin faker).

Estrategia:
- Catálogos Tier 2 (marcas, categorias, ciudades, vehiculos) se siembran NORMALIZADOS
  (lowercase/trim/sin acentos) para respetar el UNIQUE y que el find-or-create los reencuentre.
- estados es Tier 1 → se guarda con su nombre de display (se devuelve tal cual).
- productos y leads se crean con los MÉTODOS FUNCIONALES (ProductoModel.create / LeadModel.create),
  lo que además puebla las tablas de relación (productos_*, leads_*) vía find-or-create/find-or-fail.
- chats, pre_ordenes y pre_ordenes_productos se insertan directamente (sus modelos están vacíos).

Idempotente: cada bloque verifica existencia antes de insertar/crear.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import resolvers
from app.core.mixins import _now
from app.core.normalization import normalize
from app.models.chat_model import ChatModel
from app.models.ciudad_model import CiudadModel
from app.models.estado_model import EstadoModel
from app.models.lead_model import LeadModel
from app.models.pre_orden_model import PreOrdenModel
from app.models.pre_orden_producto_model import PreOrdenProductoModel
from app.models.producto_model import ProductoModel

# (display estado, [ciudades display]) — ciudad se normaliza al guardar.
ESTADOS_Y_CIUDADES = [
    ("Nuevo León", ["Monterrey"]),
    ("Jalisco", ["Guadalajara"]),
    ("Ciudad de México", ["Ciudad de México"]),
]

MARCAS = ["Nissan", "Hyundai", "Honda", "BYD", "Tesla"]
CATEGORIAS = ["baterías", "balatas", "cremalleras"]
# (modelo, marca, anio)
VEHICULOS = [
    ("Versa", "Nissan", 2015),
    ("Sentra", "Nissan", 2018),
    ("Elantra", "Hyundai", 2016),
]

# productos: precio en centavos en la moneda original. Mezcla MXN(1)/USD(2)/EUR(3).
PRODUCTOS = [
    {
        "marca": "Nissan", "modelo": "Batería LTH L-24", "precio": 189900, "moneda_id": 1,
        "stock": 10, "especificaciones": {"voltaje": "12V", "amperes_arranque_frio": "650 CCA"},
        "vehiculos": [{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
        "categorias": ["baterías"], "ciudades": ["Monterrey"],
    },
    {
        "marca": "Honda", "modelo": "Batería LTH L-42", "precio": 220000, "moneda_id": 1,
        "stock": 5, "especificaciones": {"voltaje": "12V", "amperes_arranque_frio": "750 CCA"},
        "vehiculos": [{"modelo": "Elantra", "marca": "Hyundai", "anio": 2016}],
        "categorias": ["baterías"], "ciudades": ["Guadalajara"],
    },
    {
        "marca": "Hyundai", "modelo": "Balata Delantera Brembo", "precio": 4599, "moneda_id": 2,
        "stock": 20, "especificaciones": {"material": "cerámica"},
        "vehiculos": [{"modelo": "Elantra", "marca": "Hyundai", "anio": 2016}],
        "categorias": ["balatas"], "ciudades": ["Monterrey", "Guadalajara"],
    },
    {
        "marca": "Nissan", "modelo": "Cremallera de Dirección", "precio": 12999, "moneda_id": 3,
        "stock": 3, "especificaciones": None,
        "vehiculos": [{"modelo": "Sentra", "marca": "Nissan", "anio": 2018}],
        "categorias": ["cremalleras"], "ciudades": ["Ciudad de México"],
    },
    # Dos productos con el MISMO modelo (distinta marca) para ejercitar el find-or-fail
    # multi-match de leads.productos_interes.
    {
        "marca": "BYD", "modelo": "Filtro de Aceite Universal", "precio": 29999, "moneda_id": 1,
        "stock": 50, "especificaciones": {"rosca": "M20"},
        "vehiculos": [], "categorias": [], "ciudades": ["Monterrey"],
    },
    {
        "marca": "Tesla", "modelo": "Filtro de Aceite Universal", "precio": 31999, "moneda_id": 2,
        "stock": 40, "especificaciones": {"rosca": "M20"},
        "vehiculos": [], "categorias": [], "ciudades": ["Guadalajara"],
    },
]

# leads: ciudad/productos_interes find-or-fail; vehiculo find-or-create.
LEADS = [
    {
        "chat_whatsapp_id": "5218110000001@c.us", "nombre_whatsapp": "Juan Pérez",
        "telefono": "+528110000001", "nombre": "Juan", "ciudad": "Monterrey",
        "productos_interes": ["Batería LTH L-24"],
        "vehiculo": [{"modelo": "Versa", "marca": "Nissan", "anio": 2015}],
        "direccion_envio": "Av. Constitución 100, Monterrey", "intencion_de_compra_id": 3,
    },
    {
        "chat_whatsapp_id": "5213330000002@c.us", "nombre_whatsapp": "María López",
        "telefono": "+523330000002", "nombre": "María", "ciudad": "Guadalajara",
        # modelo con doble match → se persisten 2 filas en leads_productos
        "productos_interes": ["Filtro de Aceite Universal"],
        "vehiculo": [{"modelo": "Elantra", "marca": "Hyundai", "anio": 2016}],
        "direccion_envio": None, "intencion_de_compra_id": 2,
    },
    {
        "chat_whatsapp_id": "5215550000003@c.us", "nombre_whatsapp": "Carlos Ruiz",
        "telefono": "+525550000003", "nombre": None, "ciudad": "Ciudad de México",
        "productos_interes": ["Cremallera de Dirección"],
        "vehiculo": [{"modelo": "Sentra", "marca": "Nissan", "anio": 2018}],
        "direccion_envio": "Reforma 222, CDMX", "intencion_de_compra_id": 4,
    },
]


def _get_or_create_estado(db: Session, nombre: str) -> EstadoModel:
    row = db.scalar(select(EstadoModel).where(EstadoModel.estado == nombre, EstadoModel.deleted_at.is_(None)))
    if row is None:
        ts = _now()
        row = EstadoModel(estado=nombre, created_at=ts, updated_at=ts)
        db.add(row)
        db.flush()
    return row


def _get_or_create_ciudad(db: Session, ciudad: str, estado_id: int) -> CiudadModel:
    nombre = normalize(ciudad)
    row = db.scalar(select(CiudadModel).where(CiudadModel.ciudad == nombre, CiudadModel.deleted_at.is_(None)))
    if row is None:
        ts = _now()
        row = CiudadModel(ciudad=nombre, estado_id=estado_id, created_at=ts, updated_at=ts)
        db.add(row)
        db.flush()
    return row


def seed(db: Session) -> None:
    # 1) estados + ciudades (Tier 1 display / Tier 2 normalizado)
    for estado_nombre, ciudades in ESTADOS_Y_CIUDADES:
        estado = _get_or_create_estado(db, estado_nombre)
        for ciudad in ciudades:
            _get_or_create_ciudad(db, ciudad, estado.id)

    # 2) catálogos Tier 2 normalizados (find-or-create idempotente)
    for marca in MARCAS:
        resolvers.find_or_create_marca(db, marca)
    for categoria in CATEGORIAS:
        resolvers.find_or_create_categoria(db, categoria)
    for modelo, marca, anio in VEHICULOS:
        resolvers.find_or_create_vehiculo(db, modelo, marca, anio)
    db.commit()

    # 3) productos vía ProductoModel.create (puebla productos_* por find-or-create)
    for p in PRODUCTOS:
        existe = db.scalar(
            select(ProductoModel).where(
                ProductoModel.modelo == p["modelo"],
                ProductoModel.marca_id == resolvers.find_or_create_marca(db, p["marca"]).id,
                ProductoModel.deleted_at.is_(None),
            )
        )
        if existe is None:
            ProductoModel.create(db, **p)

    # 4) leads vía LeadModel.create (puebla leads_* por find-or-fail / find-or-create)
    for ld in LEADS:
        existe = db.scalar(
            select(LeadModel).where(
                LeadModel.chat_whatsapp_id == ld["chat_whatsapp_id"],
                LeadModel.deleted_at.is_(None),
            )
        )
        if existe is None:
            LeadModel.create(db, **ld)

    # 5) chats (1 activo por lead) + pre_ordenes + pre_ordenes_productos (inserción directa)
    ts = _now()
    leads = list(db.scalars(select(LeadModel).where(LeadModel.deleted_at.is_(None))))
    for lead in leads:
        chat_existe = db.scalar(
            select(ChatModel).where(ChatModel.lead_id == lead.id, ChatModel.deleted_at.is_(None))
        )
        if chat_existe is None:
            db.add(ChatModel(
                lead_id=lead.id, chat_whatsapp_id=lead.chat_whatsapp_id,
                chat_status_id=1, resumen=f"Conversación inicial con {lead.nombre_whatsapp}.",
                created_at=ts, updated_at=ts,
            ))

    # una pre-orden de ejemplo para el primer lead (total en MXN ya convertido)
    primer_lead = leads[0] if leads else None
    if primer_lead is not None:
        po_existe = db.scalar(
            select(PreOrdenModel).where(
                PreOrdenModel.lead_id == primer_lead.id, PreOrdenModel.deleted_at.is_(None)
            )
        )
        if po_existe is None:
            # Batería LTH L-24: 189900 centavos MXN x 1 unidad
            producto = db.scalar(
                select(ProductoModel).where(
                ProductoModel.modelo == "Batería LTH L-24",
                ProductoModel.deleted_at.is_(None),
            )
            )
            cantidad = 1
            total_mxn = producto.precio * cantidad  # ya en MXN (moneda_id=1)
            pre_orden = PreOrdenModel(
                lead_id=primer_lead.id, total=total_mxn, created_at=ts, updated_at=ts
            )
            db.add(pre_orden)
            db.flush()
            db.add(PreOrdenProductoModel(
                pre_orden_id=pre_orden.id, producto_id=producto.id, cantidad=cantidad,
                created_at=ts, updated_at=ts,
            ))

    db.commit()
