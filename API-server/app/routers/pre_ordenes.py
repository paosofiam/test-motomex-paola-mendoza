"""Router del recurso pre_ordenes: frontera HTTP (sin lógica de negocio).

Declara la ruta, valida petición/respuesta con Pydantic, fija status HTTP y header `Location`,
y documenta errores RFC 7807. La lógica vive en la capa service, aún pendiente. Responde 501.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.pre_orden import PreOrdenCreate, PreOrdenResponse

router = APIRouter(prefix="/pre_ordenes", tags=["pre_ordenes"])

_PENDING = "Ruta declarada (stub); pendiente de implementación"


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
    # SEAM (pendiente):
    #   pre_orden = pre_orden_service.create(db, payload)
    #   response.headers["Location"] = f"/pre_ordenes/{pre_orden.id}"
    #   return pre_orden
    # SERVICE: `total` persiste en MXN centavos (ya convertido por el agente antes de enviar).
    # SERVICE: verificar que producto_id existe y no está soft-deleted (NotFoundError -> 404).
    # SERVICE: construir PreOrdenResponse con productos=[{producto_id, modelo, cantidad}],
    #   resolviendo modelo=producto.modelo por cada ítem.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)
