"""Entidad Tier 3: chats — MODELO FUNCIONAL.

Métodos permitidos (matriz): get_by_id, get_by_chat_whatsapp_id, get_by_lead, create, update, delete.

Notas de contrato (el shaping de respuesta vive en la capa service, `chat_service.py`; aquí
los métodos devuelven la instancia ORM con `chat_status` cargado):
- `lead_id` y `chat_whatsapp_id` son inmutables tras crear (no se aceptan en update).
- Solo un chat activo por lead a la vez: `create` soft-deletes el chat previo del mismo lead
  antes de insertar el nuevo.
- `get_by_chat_whatsapp_id` y `get_by_lead` devuelven el chat activo más reciente
  (ORDER BY created_at DESC LIMIT 1, deleted_at IS NULL).
- `update` solo toca `chat_status_id` y `resumen`.
- `delete` es soft delete; deja intactas las filas relacionadas.
"""

from sqlalchemy import ForeignKey, Index, String, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.exceptions import NotFoundError
from app.core.mixins import TimestampMixin, _now
from app.database import Base
from app.models.chat_status_model import ChatStatusModel

# Sentinela para distinguir "campo no provisto" de "provisto = None" en update (PATCH parcial).
_UNSET = object()


class ChatModel(TimestampMixin, Base):
    __tablename__ = "chats"
    __table_args__ = (
        Index("ix_chats_chat_whatsapp_id", "chat_whatsapp_id"),
        Index("ix_chats_lead_id_created_at", "lead_id", "created_at"),
    )

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    chat_whatsapp_id: Mapped[str] = mapped_column(String(255), nullable=False)
    chat_status_id: Mapped[int] = mapped_column(ForeignKey("chat_statuses.id"), nullable=False)
    resumen: Mapped[str | None] = mapped_column(Text, nullable=True)

    chat_status: Mapped["ChatStatusModel"] = relationship(lazy="joined")

    # ---- Métodos de la matriz -------------------------------------------------

    @classmethod
    def get_by_id(cls, db: Session, chat_id: int) -> "ChatModel | None":
        """Chat activo por id, o None."""
        return db.scalar(
            select(cls).where(cls.id == chat_id, cls.deleted_at.is_(None))
        )

    @classmethod
    def get_by_chat_whatsapp_id(cls, db: Session, chat_whatsapp_id: str) -> "ChatModel | None":
        """Chat activo más reciente por chat_whatsapp_id (ORDER BY created_at DESC LIMIT 1)."""
        return db.scalar(
            select(cls)
            .where(cls.chat_whatsapp_id == chat_whatsapp_id, cls.deleted_at.is_(None))
            .order_by(cls.created_at.desc())
            .limit(1)
        )

    @classmethod
    def get_by_lead(cls, db: Session, lead_id: int) -> "ChatModel | None":
        """Chat activo más reciente del lead (ORDER BY created_at DESC LIMIT 1)."""
        return db.scalar(
            select(cls)
            .where(cls.lead_id == lead_id, cls.deleted_at.is_(None))
            .order_by(cls.created_at.desc())
            .limit(1)
        )

    @classmethod
    def create(
        cls,
        db: Session,
        *,
        lead_id: int,
        chat_whatsapp_id: str,
        chat_status_id: int,
        resumen: str | None = None,
    ) -> "ChatModel":
        """Crea un chat para el lead, soft-deleting el chat activo previo si existe.

        `lead_id` y `chat_whatsapp_id` son inmutables tras la creación.
        `created_at == updated_at`. Hace flush y devuelve el chat recién creado.
        """
        ts = _now()

        previo = cls.get_by_lead(db, lead_id)
        if previo is not None:
            previo.deleted_at = ts

        chat = cls(
            lead_id=lead_id,
            chat_whatsapp_id=chat_whatsapp_id,
            chat_status_id=chat_status_id,
            resumen=resumen,
            created_at=ts,
            updated_at=ts,
        )
        db.add(chat)
        db.flush()
        db.refresh(chat)
        return chat

    @classmethod
    def update(
        cls,
        db: Session,
        chat_id: int,
        *,
        chat_status_id=_UNSET,
        resumen=_UNSET,
    ) -> "ChatModel":
        """PATCH parcial. `lead_id` y `chat_whatsapp_id` son inmutables (no son parámetros).
        Solo actualiza los campos provistos. Refresca `updated_at`.
        """
        chat = cls.get_by_id(db, chat_id)
        if chat is None:
            raise NotFoundError("Chat", chat_id)

        if chat_status_id is not _UNSET:
            chat.chat_status_id = chat_status_id
        if resumen is not _UNSET:
            chat.resumen = resumen

        chat.updated_at = _now()
        db.refresh(chat)
        return chat

    @classmethod
    def delete(cls, db: Session, chat_id: int) -> bool:
        """Soft delete (set deleted_at). Devuelve False si no existe o ya está eliminado."""
        chat = cls.get_by_id(db, chat_id)
        if chat is None:
            return False
        chat.deleted_at = _now()
        return True
