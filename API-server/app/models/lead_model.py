"""Entidad Tier 3: leads — MODELO FUNCIONAL.

Métodos permitidos (matriz): get_by_id, search, create, update.

Notas de contrato (el shaping de respuesta vive en la capa service, `lead_service.py`; aquí
los métodos devuelven la instancia ORM con relaciones cargadas):
- `chat_id` y `estado` NO son columnas: son derivados de respuesta. `estado` se resuelve por
  `ciudad → ciudades.estado_id → estados.estado` (relación `ciudad.estado` cargada).
  `chat_id` lo provee `resolvers.get_active_chat_id` (consulta suelta).
- `chat_whatsapp_id` es inmutable tras crear (no se acepta en update).
- `ciudad` (string) es find-or-fail; `productos_interes` [string] es find-or-fail por modelo
  (un modelo puede matchear varios → se persisten todas las relaciones); `vehiculo`
  [{modelo,marca,anio}] es find-or-create (cascada marca).
- `telefono` se almacena en formato E.164 (`String(15)`).

El centinela de módulo `_UNSET` distingue "campo no provisto" de "provisto = None" en `update`
(PATCH parcial).
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core import resolvers
from app.core.mixins import TimestampMixin, _now
from app.database import Base
from app.models.intencion_de_compra_de_lead_model import IntencionDeCompraDeLeadModel
from app.models.lead_producto_model import LeadProductoModel
from app.models.lead_vehiculo_model import LeadVehiculoModel

_UNSET = object()


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

    @classmethod
    def search(
        cls,
        db: Session,
        chat_whatsapp_id: str | None = None,
        intencion_de_compra: str | None = None,
    ) -> list["LeadModel"]:
        """Leads activos con filtros opcionales por `chat_whatsapp_id` e `intencion_de_compra` (string)."""
        stmt = select(cls).where(cls.deleted_at.is_(None))
        if chat_whatsapp_id is not None:
            stmt = stmt.where(cls.chat_whatsapp_id == chat_whatsapp_id)
        if intencion_de_compra is not None:
            stmt = stmt.join(
                IntencionDeCompraDeLeadModel,
                cls.intencion_de_compra_id == IntencionDeCompraDeLeadModel.id,
            ).where(IntencionDeCompraDeLeadModel.tipo == intencion_de_compra)
        return list(db.scalars(stmt))

    @classmethod
    def create(
        cls,
        db: Session,
        *,
        chat_whatsapp_id: str,
        nombre_whatsapp: str,
        telefono: str,
        intencion_de_compra_id: int,
        nombre: str | None = None,
        ciudad: str | None = None,
        productos_interes: list[str] | None = None,
        vehiculo: list[dict] | None = None,
        direccion_envio: str | None = None,
    ) -> "LeadModel":
        """Crea un lead. `ciudad` find-or-fail; `productos_interes` find-or-fail por modelo;
        `vehiculo` find-or-create. `created_at == updated_at`. Hace commit y devuelve el lead.

        Hace `flush` de las filas de relación antes del `refresh` final: sin esto, con
        autoflush=False, la carga selectin de `leads_productos`/`leads_vehiculos` leería las
        tablas de relación aún vacías y la respuesta saldría con listas vacías.
        """
        ciudad_id = resolvers.find_ciudad_or_fail(db, ciudad).id if ciudad else None
        ts = _now()
        lead = cls(
            chat_whatsapp_id=chat_whatsapp_id,
            nombre_whatsapp=nombre_whatsapp,
            telefono=telefono,
            nombre=nombre,
            ciudad_id=ciudad_id,
            direccion_envio=direccion_envio,
            intencion_de_compra_id=intencion_de_compra_id,
            created_at=ts,
            updated_at=ts,
        )
        db.add(lead)
        db.flush()

        cls._sync_productos_interes(db, lead.id, productos_interes, ts)
        cls._sync_vehiculos(db, lead.id, vehiculo, ts)

        db.flush()
        db.refresh(lead)
        return lead

    @classmethod
    def update(
        cls,
        db: Session,
        lead_id: int,
        *,
        nombre_whatsapp=_UNSET,
        telefono=_UNSET,
        nombre=_UNSET,
        ciudad=_UNSET,
        productos_interes=_UNSET,
        vehiculo=_UNSET,
        direccion_envio=_UNSET,
        intencion_de_compra_id=_UNSET,
    ) -> "LeadModel | None":
        """PATCH parcial. `chat_whatsapp_id` es inmutable (no es parámetro). Refresca SOLO
        `updated_at`. Re-resuelve/reemplaza relaciones para los campos provistos. Devuelve `None`
        si el lead no existe o está soft-deleted (la traducción a `NotFoundError` vive en el service).

        Antes de `refresh` hace `flush` explícito (`refresh` descarta lo aún no flusheado).
        """
        lead = cls.get_by_id(db, lead_id)
        if lead is None:
            return None

        if nombre_whatsapp is not _UNSET:
            lead.nombre_whatsapp = nombre_whatsapp
        if telefono is not _UNSET:
            lead.telefono = telefono
        if nombre is not _UNSET:
            lead.nombre = nombre
        if direccion_envio is not _UNSET:
            lead.direccion_envio = direccion_envio
        if intencion_de_compra_id is not _UNSET:
            lead.intencion_de_compra_id = intencion_de_compra_id
        if ciudad is not _UNSET:
            lead.ciudad_id = resolvers.find_ciudad_or_fail(db, ciudad).id if ciudad else None

        ts = _now()
        if productos_interes is not _UNSET:
            cls._sync_productos_interes(db, lead.id, productos_interes, ts, replace=True)
        if vehiculo is not _UNSET:
            cls._sync_vehiculos(db, lead.id, vehiculo, ts, replace=True)

        lead.updated_at = ts
        db.flush()
        db.refresh(lead)
        return lead

    @staticmethod
    def _sync_link_rows(
        db: Session,
        model: type,
        lead_id: int,
        desired_ids: list[int],
        fk_name: str,
        ts: datetime,
        replace: bool,
    ) -> None:
        """Reconcilia filas de relación respetando soft-delete + UNIQUE(lead_id, fk).

        `model` es la clase ORM de la tabla de relación con columna `lead_id`
        (`LeadProductoModel` | `LeadVehiculoModel`). `desired_ids` se deduplica preservando orden.
        Reactiva filas soft-deleted que vuelven al conjunto deseado (evita violar el UNIQUE
        al re-insertar el mismo par), soft-elimina las que sobran (solo si replace=True) e
        inserta las nuevas. Nunca hard delete.
        """
        existing = {
            getattr(r, fk_name): r
            for r in db.scalars(select(model).where(model.lead_id == lead_id))
        }
        desired = list(dict.fromkeys(desired_ids))
        for fk_id in desired:
            row = existing.get(fk_id)
            if row is None:
                db.add(model(**{"lead_id": lead_id, fk_name: fk_id},
                             created_at=ts, updated_at=ts))
            elif row.deleted_at is not None:
                row.deleted_at = None
                row.updated_at = ts
        if replace:
            desired_set = set(desired)
            for fk_id, row in existing.items():
                if fk_id not in desired_set and row.deleted_at is None:
                    row.deleted_at = ts

    @classmethod
    def _sync_productos_interes(
        cls,
        db: Session,
        lead_id: int,
        productos_interes: list[str] | None,
        ts: datetime,
        replace: bool = False,
    ) -> None:
        if productos_interes is None:
            if replace:
                cls._sync_link_rows(db, LeadProductoModel, lead_id, [], "producto_id", ts, True)
            return
        producto_ids = []
        for modelo in productos_interes:
            for prod in resolvers.find_productos_by_modelo_or_fail(db, modelo):
                producto_ids.append(prod.id)
        cls._sync_link_rows(db, LeadProductoModel, lead_id, producto_ids, "producto_id", ts, replace)

    @classmethod
    def _sync_vehiculos(
        cls,
        db: Session,
        lead_id: int,
        vehiculo: list[dict] | None,
        ts: datetime,
        replace: bool = False,
    ) -> None:
        if vehiculo is None:
            if replace:
                cls._sync_link_rows(db, LeadVehiculoModel, lead_id, [], "vehiculo_id", ts, True)
            return
        vehiculo_ids = [
            resolvers.find_or_create_vehiculo(db, v["modelo"], v["marca"], v["anio"]).id
            for v in vehiculo
        ]
        cls._sync_link_rows(db, LeadVehiculoModel, lead_id, vehiculo_ids, "vehiculo_id", ts, replace)
