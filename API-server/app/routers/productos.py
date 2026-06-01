"""Router del recurso productos: frontera HTTP (sin lógica de negocio).

Declara rutas, valida petición/respuesta con Pydantic, fija status HTTP y header `Location`, y
documenta errores RFC 7807. La lógica (conversión a MXN, find-or-create de marca/vehiculos/
categorias/ciudades, persistencia) vive en `services/producto_service.py`. Las excepciones de
dominio que suban se traducen a `application/problem+json` vía los handlers registrados.
"""

from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.producto import ProductoCreate, ProductoResponse
from app.services import producto_service

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("", response_model=list[ProductoResponse])
def read_productos(
    marca: str | None = None,
    precio_minimo: int | None = None,
    db: Session = Depends(get_db),
) -> Any:
    """Lista productos activos, con filtros opcionales por `marca` y `precio_minimo`."""
    return producto_service.search(db, marca=marca, precio_minimo=precio_minimo)


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
    """Crea un producto (find-or-create de catálogos Tier 2). Devuelve 201 + header `Location`."""
    producto = producto_service.create(db, payload)
    response.headers["Location"] = f"/productos/{producto.id}"
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
