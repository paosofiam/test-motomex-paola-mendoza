"""Catálogo de las 32 entidades federativas de México (resoluble por nombre o abreviación).

Idempotente POR NOMBRE (no por id): respeta filas pre-existentes y solo inserta las entidades que
falten, rellenando la `abreviacion` de las que ya existieran sin ella. A diferencia de los catálogos
de `catalog_defaults` (Tier 1 referenciados por id en los bodies), `estados` se resuelve por string
(nombre o abreviación) en la capa service, por lo que su id es interno y no se fija.
Se guarda con el nombre de display en forma corta (p. ej. "Nuevo León", "Estado de México").
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.mixins import _now
from app.models.estado_model import EstadoModel

ESTADOS = [
    ("Aguascalientes", "AGS"),
    ("Baja California", "BC"),
    ("Baja California Sur", "BCS"),
    ("Campeche", "CAMP"),
    ("Chiapas", "CHIS"),
    ("Chihuahua", "CHIH"),
    ("Ciudad de México", "CDMX"),
    ("Coahuila", "COAH"),
    ("Colima", "COL"),
    ("Durango", "DGO"),
    ("Estado de México", "EDOMEX"),
    ("Guanajuato", "GTO"),
    ("Guerrero", "GRO"),
    ("Hidalgo", "HGO"),
    ("Jalisco", "JAL"),
    ("Michoacán", "MICH"),
    ("Morelos", "MOR"),
    ("Nayarit", "NAY"),
    ("Nuevo León", "NL"),
    ("Oaxaca", "OAX"),
    ("Puebla", "PUE"),
    ("Querétaro", "QRO"),
    ("Quintana Roo", "QROO"),
    ("San Luis Potosí", "SLP"),
    ("Sinaloa", "SIN"),
    ("Sonora", "SON"),
    ("Tabasco", "TAB"),
    ("Tamaulipas", "TAMPS"),
    ("Tlaxcala", "TLAX"),
    ("Veracruz", "VER"),
    ("Yucatán", "YUC"),
    ("Zacatecas", "ZAC"),
]


def seed(db: Session) -> None:
    """Inserta las entidades faltantes y rellena abreviaciones vacías (idempotente por nombre)."""
    ts = _now()

    for estado, abreviacion in ESTADOS:
        row = db.scalar(
            select(EstadoModel).where(EstadoModel.estado == estado, EstadoModel.deleted_at.is_(None))
        )
        if row is None:
            db.add(EstadoModel(estado=estado, abreviacion=abreviacion, created_at=ts, updated_at=ts))
        elif row.abreviacion is None:
            row.abreviacion = abreviacion
            row.updated_at = ts

    db.commit()
