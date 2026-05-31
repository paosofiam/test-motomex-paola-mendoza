"""Valores por defecto OBLIGATORIOS y EXACTOS de catálogos Tier 1 (de er_diagram.md).

Se insertan con ids explícitos. Idempotente: si el id ya existe, no lo toca.
Estos catálogos son Tier 1 → su string se devuelve tal cual en las respuestas, por lo que
NO se normalizan (p. ej. abreviacion "MXN" en mayúsculas, "en revisión" con acento).
"""

from sqlalchemy.orm import Session

from app.core.mixins import _now
from app.models.chat_status_model import ChatStatusModel
from app.models.intencion_de_compra_de_lead_model import IntencionDeCompraDeLeadModel
from app.models.moneda_model import MonedaModel

MONEDAS = [
    (1, "Pesos Mexicanos", "MXN", 100),
    (2, "Dólares", "USD", 1700),
    (3, "Euros", "EUR", 2300),
]

INTENCIONES = [
    (1, "baja"),
    (2, "media"),
    (3, "alta"),
    (4, "completa"),
]

CHAT_STATUSES = [
    (1, "activo"),
    (2, "en revisión"),
    (3, "en espera"),
    (4, "con cliente"),
    (5, "cerrado"),
]


def seed(db: Session) -> None:
    """Inserta los catálogos Tier 1 con ids exactos (idempotente)."""
    ts = _now()

    for _id, moneda, abreviacion, tipo_de_cambio in MONEDAS:
        if db.get(MonedaModel, _id) is None:
            db.add(MonedaModel(
                id=_id, moneda=moneda, abreviacion=abreviacion,
                tipo_de_cambio=tipo_de_cambio, created_at=ts, updated_at=ts,
            ))

    for _id, tipo in INTENCIONES:
        if db.get(IntencionDeCompraDeLeadModel, _id) is None:
            db.add(IntencionDeCompraDeLeadModel(
                id=_id, tipo=tipo, created_at=ts, updated_at=ts
            ))

    for _id, status in CHAT_STATUSES:
        if db.get(ChatStatusModel, _id) is None:
            db.add(ChatStatusModel(id=_id, status=status, created_at=ts, updated_at=ts))

    db.commit()
