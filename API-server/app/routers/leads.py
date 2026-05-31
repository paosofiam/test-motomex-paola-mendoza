"""Router del recurso leads: frontera HTTP (sin lógica de negocio).

Declara rutas, valida petición/respuesta con Pydantic, fija status HTTP y header `Location`, y
documenta errores RFC 7807. La lógica (find-or-fail de `ciudad`/`productos_interes`, find-or-create
de `vehiculo`, derivación de `estado` y `chat_id`, persistencia) vive en la capa service, aún
pendiente: cada cuerpo marca el SEAM donde se delegará. Hasta entonces responden 501.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])

_PENDING = "Ruta declarada; pendiente de conexión a la capa service"


@router.get("", response_model=list[LeadResponse])
def read_leads(
    chat_whatsapp_id: str | None = None,
    intencion_de_compra: str | None = None,
    db: Session = Depends(get_db),
) -> Any:
    """Lista leads activos, con filtros opcionales por `chat_whatsapp_id` e `intencion_de_compra`."""
    # SEAM (pendiente): return lead_service.search(db, chat_whatsapp_id=..., intencion_de_compra=...)
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ProblemDetail}},
)
def create_lead(
    payload: LeadCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> Any:
    """Crea un lead. Devuelve 201 + header `Location`. 422 si un string Tier 2 no resuelve."""
    # SEAM (pendiente):
    #   lead = lead_service.create(db, payload)
    #   response.headers["Location"] = f"/leads/{lead.id}"
    #   return lead
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
    responses={404: {"model": ProblemDetail}},
)
def read_lead(lead_id: int, db: Session = Depends(get_db)) -> Any:
    """Devuelve un lead activo por id, o 404 si no existe / está soft-deleted."""
    # SEAM (pendiente): return lead_service.get_by_id(db, lead_id)  # NotFoundError -> 404
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)


@router.patch(
    "/{lead_id}",
    response_model=LeadResponse,
    responses={404: {"model": ProblemDetail}, 422: {"model": ProblemDetail}},
)
def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
) -> Any:
    """Actualización parcial de un lead. Devuelve el lead completo actualizado (200)."""
    # SEAM (pendiente): return lead_service.update(db, lead_id, payload)  # solo campos enviados
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)
