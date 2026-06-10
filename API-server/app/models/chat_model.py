"""Entidad Tier 3: chats — TABLA ORM.

Definición de tabla pura: columnas + relationship `chat_status` + `get_by_id`. La query del chat
activo más reciente (`ORDER BY created_at DESC LIMIT 1`), la creación idempotente, el update y el
delete viven en `chat_service.py`; el modelo no filtra ni orquesta.

Notas de contrato (resueltas en la capa service):
- `lead_id` y `chat_whatsapp_id` son inmutables tras crear (no se aceptan en update).
- Solo un chat activo por `chat_whatsapp_id` a la vez: `create` es idempotente (si ya hay un chat
  activo con el mismo `lead_id` o `chat_whatsapp_id`, devuelve el existente sin crear ni borrar).
  Reemplazar un chat exige `delete` previo; `create` nunca elimina el anterior.
- `update` solo toca `chat_status_id` y `resumen`. `delete` es soft delete; deja intactas las filas
  relacionadas.
"""

from sqlalchemy import ForeignKey, Index, String, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.core.mixins import TimestampMixin
from app.database import Base
from app.models.chat_status_model import ChatStatusModel


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

    @classmethod
    def get_by_id(cls, db: Session, chat_id: int) -> "ChatModel | None":
        """Chat activo por id, o None."""
        return db.scalar(select(cls).where(cls.id == chat_id, cls.deleted_at.is_(None)))
