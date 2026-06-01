"""Capa de orquestación del recurso productos (router → service → model).

Media entre `routers/productos.py` y `ProductoModel`: recibe los schemas ya validados por
Pydantic, llama a los métodos de la matriz del modelo y construye el `ProductoResponse` que el
router devuelve por HTTP. No conoce FastAPI (sin `HTTPException`/`status`) ni gestiona la
transacción (el commit lo hace `get_db`); solo lanza excepciones de dominio (`NotFoundError`),
que `core/error_handlers.py` traduce a RFC 7807.

Construcción de la respuesta (`endpoints.md`): `precio` SIEMPRE en MXN centavos
(`round(precio * tipo_de_cambio / 100)`) y `moneda` como string (`abreviacion`).
"""

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ResolutionError
from app.models.moneda_model import MonedaModel
from app.models.producto_model import ProductoModel
from app.schemas.producto import ProductoCreate, ProductoResponse


def _to_response(producto: ProductoModel) -> ProductoResponse:
    """Convierte la instancia ORM al DTO de respuesta, con precio convertido a MXN centavos.

    `moneda` SIEMPRE es "MXN": como `precio` se entrega convertido a pesos
    (`round(precio * tipo_de_cambio / 100)`), devolver la abreviación original (USD/EUR) junto a un
    precio ya en MXN confundiría al consumidor LLM. La moneda original vive en `producto.moneda_id`.
    """
    return ProductoResponse(
        id=producto.id,
        marca=producto.marca.marca,
        modelo=producto.modelo,
        precio=round(producto.precio * producto.moneda.tipo_de_cambio / 100),
        moneda="MXN",
        stock=producto.stock,
        especificaciones=producto.especificaciones,
    )


def search(
    db: Session,
    marca: str | None = None,
    precio_minimo: int | None = None,
) -> list[ProductoResponse]:
    """Lista productos activos, con filtros opcionales por `marca` y `precio_minimo` (MXN)."""
    return [_to_response(p) for p in ProductoModel.search(db, marca=marca, precio_minimo=precio_minimo)]


def get_by_id(db: Session, producto_id: int) -> ProductoResponse:
    """Producto activo por id. Lanza `NotFoundError` (→ 404) si no existe o está soft-deleted."""
    producto = ProductoModel.get_by_id(db, producto_id)
    if producto is None:
        raise NotFoundError("Producto", producto_id)
    return _to_response(producto)


def create(db: Session, payload: ProductoCreate) -> ProductoResponse:
    """Crea un producto (find-or-create de catálogos Tier 2). `model_dump()` ya convierte
    `vehiculos` a `list[dict]`; los campos de `ProductoCreate` coinciden con los kwargs de `create`.

    `moneda_id` es Tier 1 (catálogo): si el id no resuelve, se lanza `ResolutionError` (→ 422 con
    `field`/`value_received`) en vez de dejar fallar la FK (que daría un 500 opaco).
    """
    if MonedaModel.get_by_id(db, payload.moneda_id) is None:
        raise ResolutionError(field="moneda_id", value_received=payload.moneda_id)
    producto = ProductoModel.create(db, **payload.model_dump())
    return _to_response(producto)


def delete(db: Session, producto_id: int) -> None:
    """Soft-delete del producto. Lanza `NotFoundError` (→ 404) si no existe."""
    if not ProductoModel.delete(db, producto_id):
        raise NotFoundError("Producto", producto_id)
