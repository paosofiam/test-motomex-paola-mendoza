"""Router del recurso leads: frontera HTTP (sin lógica de negocio).

Declara rutas, valida petición/respuesta con Pydantic, fija status HTTP y header `Location`, y
documenta errores RFC 7807. La lógica (resolución con éxito parcial de `ciudad` y `productos_interes`
—find-or-skip aditivo—, find-or-create de `vehiculo`, derivación de `estado` y `chat_id`,
persistencia) vive en `services/lead_service.py`. Las excepciones de dominio que suban se traducen a
`application/problem+json` vía los handlers.
"""

from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.error_handlers import warning_header
from app.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from app.services import lead_service

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=list[LeadResponse])
def read_leads(
    chat_whatsapp_id: str | None = None,
    intencion_de_compra: str | None = None,
    db: Session = Depends(get_db),
) -> Any:
    """Lista leads activos, con filtros opcionales por `chat_whatsapp_id` e `intencion_de_compra`."""
    return lead_service.search(
        db, chat_whatsapp_id=chat_whatsapp_id, intencion_de_compra=intencion_de_compra
    )


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
    """Crea un lead. Devuelve 201 + header `Location`. 422 solo si `intencion_de_compra_id` (Tier 1)
    no resuelve o el `telefono` no es E.164. La ciudad (estado no reconocido) o los productos de interés
    (modelo inexistente en inventario) que no se pudieron vincular se informan en el header `Warning`;
    el lead se crea igual."""
    lead, avisos = lead_service.create(db, payload)
    response.headers["Location"] = f"/leads/{lead.id}"
    if avisos:
        response.headers["Warning"] = warning_header(avisos)
    return lead


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
    responses={404: {"model": ProblemDetail}},
)
def read_lead(lead_id: int, db: Session = Depends(get_db)) -> Any:
    """Devuelve un lead activo por id, o 404 si no existe / está soft-deleted."""
    return lead_service.get_by_id(db, lead_id)


@router.patch(
    "/{lead_id}",
    response_model=LeadResponse,
    responses={404: {"model": ProblemDetail}, 422: {"model": ProblemDetail}},
)
def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    response: Response,
    db: Session = Depends(get_db),
) -> Any:
    """Actualización parcial de un lead. Devuelve el lead completo actualizado (200). `productos_interes`
    y `vehiculo` se vinculan de forma aditiva (combinan con lo existente; vacío/omitido = sin cambios).
    La ciudad (estado no reconocido) o los productos de interés (modelo inexistente) que no se pudieron
    vincular se informan en el header `Warning`."""
    lead, avisos = lead_service.update(db, lead_id, payload)
    if avisos:
        response.headers["Warning"] = warning_header(avisos)
    return lead
