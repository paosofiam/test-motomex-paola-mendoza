"""Entidad Tier 3: leads — TABLA ORM.

Definición de tabla pura: columnas + relationships + `get_by_id`. La consulta por `chat_whatsapp_id`
(un solo objeto), la creación idempotente/actualización con resolución de catálogos y la
reconciliación de las tablas de relación viven en `lead_service.py` (+ `core/resolvers.py`); el
modelo no filtra ni orquesta.

Notas de contrato (resueltas en la capa service):
- `chat_id`, `status` y `estado` NO son columnas: son derivados de respuesta. `estado` se resuelve por
  `ciudad → ciudades.estado_id → estados.estado` (relación `ciudad.estado` cargada); `chat_id` y
  `status` los provee `resolvers.get_active_chat` (chat activo, consulta suelta).
- `chat_whatsapp_id` es inmutable tras crear (no se acepta en update) y es la clave de unicidad: solo
  un lead activo por `chat_whatsapp_id` a la vez (`create` es idempotente; los leads no se borran vía
  API).
- `ciudad_id` llega ya resuelto desde `lead_service` (que aplica éxito parcial sobre el objeto
  `{ciudad, estado}`); `productos_interes` [string] es find-or-skip aditivo por modelo (un modelo
  puede matchear varios → se persisten todas las relaciones; los modelos sin match en inventario se
  omiten con aviso, sin bloquear el lead); `vehiculo` [{modelo,marca,anio}] es find-or-create
  (cascada marca). En `PATCH`, `productos_interes` y `vehiculo` se vinculan de forma aditiva
  (combinan con lo existente, sin reemplazar ni borrar).
- `telefono` se almacena en formato E.164 (`String(15)`).
"""

from sqlalchemy import ForeignKey, Index, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.mixins import TimestampMixin
from app.database import Base
from app.models.lead_producto_model import LeadProductoModel
from app.models.lead_vehiculo_model import LeadVehiculoModel


class LeadModel(TimestampMixin, Base):
    __tablename__ = "leads"
    __table_args__ = (Index("ix_leads_chat_whatsapp_id", "chat_whatsapp_id"),)

    chat_whatsapp_id: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_whatsapp: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str] = mapped_column(String(15), nullable=False)
    nombre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ciudad_id: Mapped[int | None] = mapped_column(ForeignKey("ciudades.id"), nullable=True)
    direccion_envio: Mapped[str | None] = mapped_column(String(512), nullable=True)
    intencion_de_compra_id: Mapped[int] = mapped_column(
        ForeignKey("intenciones_de_compra_de_leads.id"), nullable=False
    )

    ciudad: Mapped["CiudadModel | None"] = relationship(lazy="joined")  # noqa: F821
    intencion: Mapped["IntencionDeCompraDeLeadModel"] = relationship(  # noqa: F821
        foreign_keys=[intencion_de_compra_id], lazy="joined"
    )
    leads_productos: Mapped[list["LeadProductoModel"]] = relationship(
        primaryjoin=lambda: (LeadModel.id == LeadProductoModel.lead_id)
        & (LeadProductoModel.deleted_at.is_(None)),
        viewonly=True,
        lazy="selectin",
    )
    leads_vehiculos: Mapped[list["LeadVehiculoModel"]] = relationship(
        primaryjoin=lambda: (LeadModel.id == LeadVehiculoModel.lead_id)
        & (LeadVehiculoModel.deleted_at.is_(None)),
        viewonly=True,
        lazy="selectin",
    )

    @classmethod
    def get_by_id(cls, db: Session, lead_id: int) -> "LeadModel | None":
        """Lead activo por id (con relaciones cargadas), o None."""
        return db.scalar(select(cls).where(cls.id == lead_id, cls.deleted_at.is_(None)))
