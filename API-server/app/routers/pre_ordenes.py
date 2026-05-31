"""Router stub del recurso pre_ordenes: ruta declarada, schema y lógica pendientes.

`POST /pre_ordenes` exige `producto_id` exacto (sin resolución por string) y persiste `total` ya
convertido a MXN; esa lógica se implementará al completar el recurso. Responde 501.
"""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/pre_ordenes", tags=["pre_ordenes"])

_PENDING = "Ruta declarada (stub); pendiente de implementación"


@router.post("", status_code=status.HTTP_201_CREATED)
def create_pre_orden():
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, _PENDING)
