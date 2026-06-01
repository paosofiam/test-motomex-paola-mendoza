"""Router del recurso pre_ordenes: frontera HTTP (sin lógica de negocio).

Declara la ruta, valida petición/respuesta con Pydantic, fija status HTTP y header `Location`,
y documenta errores RFC 7807. La lógica de negocio vive en `services/pre_orden_service.py`.
"""

from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.pre_orden import PreOrdenCreate, PreOrdenResponse
from app.services import pre_orden_service

router = APIRouter(prefix="/pre_ordenes", tags=["pre_ordenes"])


@router.post(
    "",
    response_model=PreOrdenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ProblemDetail}, 422: {"model": ProblemDetail}},
)
def create_pre_orden(
    payload: PreOrdenCreate, response: Response, db: Session = Depends(get_db)
) -> Any:
    """Crea una pre-orden. `producto_id` exacto requerido (sin resolución por string). Devuelve 201 + Location."""
    # SERVICE (pendiente en services/pre_orden_service.py):
    #   - Validar que lead_id existe (→ NotFoundError → 404)
    #   - Validar cada producto_id exacto (Tier 3: sin resolución por string ni find-or-create)
    #     → NotFoundError → 404 si no existe o está soft-deleted
    #   - total llega ya en MXN centavos; NO se convierte (el agente LLM lo convierte antes de enviar)
    #   - Respuesta incluye modelo derivado de producto.modelo por cada ítem (join en la capa model)
    pre_orden = pre_orden_service.create(db, payload)
    response.headers["Location"] = f"/pre_ordenes/{pre_orden.id}"
    return pre_orden
