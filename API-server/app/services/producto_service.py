"""Capa de orquestación del recurso productos (router → service → model).

Media entre `routers/productos.py` y `ProductoModel`: recibe los schemas ya validados por
Pydantic, llama a los métodos de la matriz del modelo y construye el `ProductoResponse` que el
router devuelve por HTTP. No conoce FastAPI (sin `HTTPException`/`status`) ni gestiona la
transacción (el commit lo hace `get_db`); solo lanza excepciones de dominio (`NotFoundError`),
que `core/error_handlers.py` traduce a RFC 7807.

Aquí vive la resolución y vinculación de `ciudades` ({ciudad, estado}): tras crear el producto, se
resuelven con éxito parcial (`resolvers.resolver_ciudades`) y se escriben las filas de
`productos_ciudades`; los avisos de ciudades omitidas suben al router (header `Warning`).

Construcción de la respuesta (`endpoints.md`): recurso completo (incluye `vehiculos`, `categorias`
y `ciudades` persistidas). `precio` SIEMPRE en MXN centavos (`round(precio * tipo_de_cambio / 100)`)
y `moneda` como string (`abreviacion`).
"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import resolvers
from app.core.exceptions import NotFoundError, ResolutionError
from app.core.mixins import _now
from app.core.normalization import normalize
from app.models.categoria_model import CategoriaModel
from app.models.ciudad_model import CiudadModel
from app.models.marca_model import MarcaModel
from app.models.moneda_model import MonedaModel
from app.models.producto_categoria_model import ProductoCategoriaModel
from app.models.producto_ciudad_model import ProductoCiudadModel
from app.models.producto_model import ProductoModel
from app.models.producto_vehiculo_model import ProductoVehiculoModel
from app.models.vehiculo_model import VehiculoModel
from app.schemas.common import CiudadEstadoSchema, VehiculoSchema
from app.schemas.producto import ProductoCreate, ProductoResponse


def _to_response(db: Session, producto: ProductoModel) -> ProductoResponse:
    """Convierte la instancia ORM al DTO de respuesta (recurso completo), con precio en MXN centavos.

    Las relaciones (`vehiculos`, `categorias`, `ciudades`) se leen con consultas explícitas sobre
    las tablas de relación, filtrando `deleted_at IS NULL`. `moneda` SIEMPRE es "MXN": como `precio`
    se entrega convertido a pesos (`round(precio * tipo_de_cambio / 100)`), devolver la abreviación
    original (USD/EUR) junto a un precio ya en MXN confundiría al consumidor LLM.
    """
    vehiculos = db.scalars(
        select(VehiculoModel)
        .join(ProductoVehiculoModel, ProductoVehiculoModel.vehiculo_id == VehiculoModel.id)
        .where(
            ProductoVehiculoModel.producto_id == producto.id,
            ProductoVehiculoModel.deleted_at.is_(None),
        )
    )
    categorias = db.scalars(
        select(CategoriaModel)
        .join(ProductoCategoriaModel, ProductoCategoriaModel.categoria_id == CategoriaModel.id)
        .where(
            ProductoCategoriaModel.producto_id == producto.id,
            ProductoCategoriaModel.deleted_at.is_(None),
        )
    )
    ciudades = db.scalars(
        select(CiudadModel)
        .join(ProductoCiudadModel, ProductoCiudadModel.ciudad_id == CiudadModel.id)
        .where(
            ProductoCiudadModel.producto_id == producto.id,
            ProductoCiudadModel.deleted_at.is_(None),
        )
    )
    return ProductoResponse(
        id=producto.id,
        marca=producto.marca.marca,
        modelo=producto.modelo,
        precio=round(producto.precio * producto.moneda.tipo_de_cambio / 100),
        moneda="MXN",
        stock=producto.stock,
        especificaciones=producto.especificaciones,
        vehiculos=[
            VehiculoSchema(modelo=v.modelo, marca=v.marca.marca, anio=v.anio) for v in vehiculos
        ],
        categorias=[c.categoria for c in categorias],
        ciudades=[
            CiudadEstadoSchema(ciudad=ci.ciudad, estado=ci.estado.estado) for ci in ciudades
        ],
    )


def search(
    db: Session,
    *,
    id: int | None = None,
    marca: str | None = None,
    modelo: str | None = None,
    precio_minimo: int | None = None,
    precio_maximo: int | None = None,
    moneda_id: int | None = None,
    stock_minimo: int | None = None,
    stock_maximo: int | None = None,
    espec_clave: str | None = None,
    espec_valor: str | None = None,
    creado_desde: datetime | None = None,
    creado_hasta: datetime | None = None,
    actualizado_desde: datetime | None = None,
    actualizado_hasta: datetime | None = None,
    categoria: str | None = None,
    ciudad: str | None = None,
    estado: str | None = None,
    vehiculo_modelo: str | None = None,
    vehiculo_marca: str | None = None,
    vehiculo_anio: int | None = None,
    order_by: str = "id",
    orden: str = "asc",
    limit: int | None = None,
    offset: int = 0,
) -> list[ProductoResponse]:
    """Lista productos activos aplicando cualquier combinación de filtros (todos AND-eados).

    Esta función es el dueño ÚNICO del filtrado de productos: construye y ejecuta aquí la query
    completa (mismo patrón que `_to_response` y `core/resolvers.py`, que consultan BD directamente),
    en vez de delegar en `ProductoModel.search`. Reglas de los filtros:
    - Catálogos Tier 2 (`marca`, `categoria`, `ciudad`, `vehiculo_marca`): match EXACTO sobre el
      valor normalizado (son UNIQUE). Texto libre (`modelo`, `vehiculo_modelo`): coincidencia
      PARCIAL "contiene" (`LIKE %x%`) sobre el término normalizado (la colación `utf8mb4_unicode_ci`
      cubre may/min y acentos del valor almacenado).
    - `precio_minimo`/`precio_maximo` comparan contra el precio ya convertido a MXN centavos
      (`round(precio * tipo_de_cambio / 100)`), vía JOIN con `monedas`.
    - Relaciones N:M (`categoria`, `ciudad`, `estado`, `vehiculo_*`) se filtran con subconsultas
      `IN` sobre las tablas de relación (no JOIN al principal) para no multiplicar filas y permitir
      combinarlas con AND sin `distinct`. Los tres `vehiculo_*` estrechan el MISMO vehículo.
    - Un valor de catálogo Tier 2 que no resuelve no es error: produce simplemente lista vacía.
    - Todo filtra `deleted_at IS NULL`.
    """
    needs_moneda = (
        precio_minimo is not None or precio_maximo is not None or order_by == "precio"
    )
    mxn = func.round(ProductoModel.precio * MonedaModel.tipo_de_cambio / 100.0)

    stmt = select(ProductoModel).where(ProductoModel.deleted_at.is_(None))
    if needs_moneda:
        stmt = stmt.join(MonedaModel, ProductoModel.moneda_id == MonedaModel.id)

    conditions = []
    if id is not None:
        conditions.append(ProductoModel.id == id)
    if marca is not None:
        conditions.append(
            ProductoModel.marca_id.in_(
                select(MarcaModel.id).where(
                    MarcaModel.marca == normalize(marca),
                    MarcaModel.deleted_at.is_(None),
                )
            )
        )
    if modelo is not None:
        conditions.append(ProductoModel.modelo.like(f"%{normalize(modelo)}%"))
    if precio_minimo is not None:
        conditions.append(mxn >= precio_minimo)
    if precio_maximo is not None:
        conditions.append(mxn <= precio_maximo)
    if moneda_id is not None:
        conditions.append(ProductoModel.moneda_id == moneda_id)
    if stock_minimo is not None:
        conditions.append(ProductoModel.stock >= stock_minimo)
    if stock_maximo is not None:
        conditions.append(ProductoModel.stock <= stock_maximo)
    if espec_clave is not None and espec_valor is not None:
        conditions.append(
            func.json_unquote(
                func.json_extract(ProductoModel.especificaciones, f"$.{espec_clave}")
            )
            == espec_valor
        )
    if creado_desde is not None:
        conditions.append(ProductoModel.created_at >= creado_desde)
    if creado_hasta is not None:
        conditions.append(ProductoModel.created_at <= creado_hasta)
    if actualizado_desde is not None:
        conditions.append(ProductoModel.updated_at >= actualizado_desde)
    if actualizado_hasta is not None:
        conditions.append(ProductoModel.updated_at <= actualizado_hasta)
    if categoria is not None:
        conditions.append(
            ProductoModel.id.in_(
                select(ProductoCategoriaModel.producto_id)
                .join(CategoriaModel, ProductoCategoriaModel.categoria_id == CategoriaModel.id)
                .where(
                    CategoriaModel.categoria == normalize(categoria),
                    ProductoCategoriaModel.deleted_at.is_(None),
                    CategoriaModel.deleted_at.is_(None),
                )
            )
        )
    if ciudad is not None:
        conditions.append(
            ProductoModel.id.in_(
                select(ProductoCiudadModel.producto_id)
                .join(CiudadModel, ProductoCiudadModel.ciudad_id == CiudadModel.id)
                .where(
                    CiudadModel.ciudad == normalize(ciudad),
                    ProductoCiudadModel.deleted_at.is_(None),
                    CiudadModel.deleted_at.is_(None),
                )
            )
        )
    if estado is not None:
        estado_row = resolvers.find_estado(db, estado)
        if estado_row is None:
            return []
        conditions.append(
            ProductoModel.id.in_(
                select(ProductoCiudadModel.producto_id)
                .join(CiudadModel, ProductoCiudadModel.ciudad_id == CiudadModel.id)
                .where(
                    CiudadModel.estado_id == estado_row.id,
                    ProductoCiudadModel.deleted_at.is_(None),
                    CiudadModel.deleted_at.is_(None),
                )
            )
        )
    if vehiculo_modelo is not None or vehiculo_marca is not None or vehiculo_anio is not None:
        veh = (
            select(ProductoVehiculoModel.producto_id)
            .join(VehiculoModel, ProductoVehiculoModel.vehiculo_id == VehiculoModel.id)
            .where(
                ProductoVehiculoModel.deleted_at.is_(None),
                VehiculoModel.deleted_at.is_(None),
            )
        )
        if vehiculo_modelo is not None:
            veh = veh.where(VehiculoModel.modelo.like(f"%{normalize(vehiculo_modelo)}%"))
        if vehiculo_marca is not None:
            veh = veh.where(
                VehiculoModel.marca_id.in_(
                    select(MarcaModel.id).where(
                        MarcaModel.marca == normalize(vehiculo_marca),
                        MarcaModel.deleted_at.is_(None),
                    )
                )
            )
        if vehiculo_anio is not None:
            veh = veh.where(VehiculoModel.anio == vehiculo_anio)
        conditions.append(ProductoModel.id.in_(veh))

    if conditions:
        stmt = stmt.where(*conditions)

    columnas = {
        "id": ProductoModel.id,
        "stock": ProductoModel.stock,
        "modelo": ProductoModel.modelo,
        "created_at": ProductoModel.created_at,
        "updated_at": ProductoModel.updated_at,
    }
    if order_by == "precio":
        orden_expr = mxn
    elif order_by == "marca":
        stmt = stmt.join(MarcaModel, ProductoModel.marca_id == MarcaModel.id)
        orden_expr = MarcaModel.marca
    else:
        orden_expr = columnas.get(order_by, ProductoModel.id)
    stmt = stmt.order_by(orden_expr.desc() if orden == "desc" else orden_expr.asc())

    if offset:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)

    return [_to_response(db, p) for p in db.scalars(stmt)]


def get_by_id(db: Session, producto_id: int) -> ProductoResponse:
    """Producto activo por id. Lanza `NotFoundError` (→ 404) si no existe o está soft-deleted."""
    producto = ProductoModel.get_by_id(db, producto_id)
    if producto is None:
        raise NotFoundError("Producto", producto_id)
    return _to_response(db, producto)


def create(db: Session, payload: ProductoCreate) -> tuple[ProductoResponse, list[str]]:
    """Crea un producto, resuelve sus catálogos conversacionales y vincula sus relaciones.

    `moneda_id` es Tier 1 (catálogo): si el id no resuelve, se lanza `ResolutionError` (→ 422 con
    `field`/`value_received`) en vez de dejar fallar la FK (que daría un 500 opaco). `marca`,
    `vehiculos` (cascada marca) y `categorias` son find-or-create; las `ciudades` ({ciudad, estado})
    se resuelven con éxito parcial: las que su estado no se reconoce se omiten y se reportan como
    avisos (el producto se crea igual). Devuelve `(respuesta, avisos)`.

    `db.flush()` de las filas de relación ANTES del `db.refresh(producto)`. `created_at == updated_at`.
    """
    if MonedaModel.get_by_id(db, payload.moneda_id) is None:
        raise ResolutionError(field="moneda_id", value_received=payload.moneda_id)
    data = payload.model_dump()
    ciudades = data.pop("ciudades")
    vehiculos = data.pop("vehiculos")
    categorias = data.pop("categorias")
    marca = data.pop("marca")

    marca_row = resolvers.find_or_create_marca(db, marca)
    ts = _now()
    producto = ProductoModel(marca_id=marca_row.id, **data, created_at=ts, updated_at=ts)
    db.add(producto)
    db.flush()

    for v in vehiculos:
        veh = resolvers.find_or_create_vehiculo(db, v["modelo"], v["marca"], v["anio"])
        db.add(ProductoVehiculoModel(
            producto_id=producto.id, vehiculo_id=veh.id, created_at=ts, updated_at=ts
        ))
    for c in categorias:
        cat = resolvers.find_or_create_categoria(db, c)
        db.add(ProductoCategoriaModel(
            producto_id=producto.id, categoria_id=cat.id, created_at=ts, updated_at=ts
        ))

    resueltas, avisos = resolvers.resolver_ciudades(db, ciudades)
    for ciudad in resueltas:
        db.add(ProductoCiudadModel(
            producto_id=producto.id, ciudad_id=ciudad.id, created_at=ts, updated_at=ts
        ))

    db.flush()
    db.refresh(producto)
    return _to_response(db, producto), avisos


def delete(db: Session, producto_id: int) -> None:
    """Soft-delete del producto. Lanza `NotFoundError` (→ 404) si no existe. No toca relaciones."""
    producto = ProductoModel.get_by_id(db, producto_id)
    if producto is None:
        raise NotFoundError("Producto", producto_id)
    producto.deleted_at = _now()
