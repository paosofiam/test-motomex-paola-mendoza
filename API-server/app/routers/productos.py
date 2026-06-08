"""Router del recurso productos: frontera HTTP (sin lógica de negocio).

Declara rutas, valida petición/respuesta con Pydantic, fija status HTTP y header `Location`, y
documenta errores RFC 7807. La lógica (conversión a MXN, find-or-create de marca/vehiculos/
categorias/ciudades, persistencia) vive en `services/producto_service.py`. Las excepciones de
dominio que suban se traducen a `application/problem+json` vía los handlers registrados.
"""

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.error_handlers import warning_header
from app.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.producto import ProductoCreate, ProductoResponse
from app.services import producto_service

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("", response_model=list[ProductoResponse])
def read_productos(
    id: int | None = Query(None, description="Filtra por id exacto del producto."),
    marca: str | None = Query(None, description="Marca (Tier 2): match exacto normalizado."),
    modelo: str | None = Query(None, description="Modelo: coincidencia parcial 'contiene'."),
    precio_minimo: int | None = Query(None, description="Precio mínimo en MXN centavos (>=)."),
    precio_maximo: int | None = Query(None, description="Precio máximo en MXN centavos (<=)."),
    moneda_id: int | None = Query(None, description="Moneda original del producto (Tier 1)."),
    stock_minimo: int | None = Query(None, description="Stock mínimo (>=)."),
    stock_maximo: int | None = Query(None, description="Stock máximo (<=)."),
    espec_clave: str | None = Query(None, description="Clave dentro de `especificaciones` (JSON)."),
    espec_valor: str | None = Query(None, description="Valor exacto para `espec_clave`."),
    creado_desde: datetime | None = Query(None, description="created_at >= (ISO 8601)."),
    creado_hasta: datetime | None = Query(None, description="created_at <= (ISO 8601)."),
    actualizado_desde: datetime | None = Query(None, description="updated_at >= (ISO 8601)."),
    actualizado_hasta: datetime | None = Query(None, description="updated_at <= (ISO 8601)."),
    categoria: str | None = Query(None, description="Categoría (Tier 2): match exacto normalizado."),
    ciudad: str | None = Query(None, description="Ciudad con disponibilidad (Tier 2): exacto normalizado."),
    estado: str | None = Query(None, description="Estado (nombre o abreviación) con disponibilidad."),
    vehiculo_modelo: str | None = Query(None, description="Modelo de vehículo compatible: parcial 'contiene'."),
    vehiculo_marca: str | None = Query(None, description="Marca de vehículo compatible (Tier 2): exacto normalizado."),
    vehiculo_anio: int | None = Query(None, description="Año de vehículo compatible: exacto."),
    order_by: Literal["id", "precio", "stock", "modelo", "marca", "created_at", "updated_at"] = Query(
        "id", description="Campo de ordenamiento."
    ),
    orden: Literal["asc", "desc"] = Query("asc", description="Dirección del ordenamiento."),
    limit: int | None = Query(None, ge=1, description="Máximo de resultados (paginación)."),
    offset: int = Query(0, ge=0, description="Desplazamiento (paginación)."),
    db: Session = Depends(get_db),
) -> Any:
    """Lista productos activos. Todos los filtros son opcionales y combinables entre sí (AND).

    Cubre columnas de `productos`, sus relaciones N:M (categorías, ciudades, vehículos
    compatibles) y el estado de disponibilidad, además de ordenamiento y paginación. Un filtro
    de catálogo Tier 2 que no resuelve no es error: devuelve lista vacía. Precios siempre en MXN.
    """
    return producto_service.search(
        db,
        id=id,
        marca=marca,
        modelo=modelo,
        precio_minimo=precio_minimo,
        precio_maximo=precio_maximo,
        moneda_id=moneda_id,
        stock_minimo=stock_minimo,
        stock_maximo=stock_maximo,
        espec_clave=espec_clave,
        espec_valor=espec_valor,
        creado_desde=creado_desde,
        creado_hasta=creado_hasta,
        actualizado_desde=actualizado_desde,
        actualizado_hasta=actualizado_hasta,
        categoria=categoria,
        ciudad=ciudad,
        estado=estado,
        vehiculo_modelo=vehiculo_modelo,
        vehiculo_marca=vehiculo_marca,
        vehiculo_anio=vehiculo_anio,
        order_by=order_by,
        orden=orden,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ProblemDetail}},
)
def create_producto(
    payload: ProductoCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> Any:
    """Crea un producto (find-or-create de catálogos Tier 2). Devuelve 201 + header `Location`.
    Si alguna ciudad no se pudo guardar (estado no reconocido), lo informa en el header `Warning`."""
    producto, avisos = producto_service.create(db, payload)
    response.headers["Location"] = f"/productos/{producto.id}"
    if avisos:
        response.headers["Warning"] = warning_header(avisos)
    return producto


@router.get(
    "/{producto_id}",
    response_model=ProductoResponse,
    responses={404: {"model": ProblemDetail}},
)
def read_producto(producto_id: int, db: Session = Depends(get_db)) -> Any:
    """Devuelve un producto activo por id, o 404 si no existe / está soft-deleted."""
    return producto_service.get_by_id(db, producto_id)


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ProblemDetail}},
)
def delete_producto(producto_id: int, db: Session = Depends(get_db)) -> None:
    """Soft-delete de un producto (set `deleted_at`). 204 sin body; 404 si no existe."""
    producto_service.delete(db, producto_id)
