"""Entidad Tier 3: chats. Sin métodos (pendiente — se desarrollará tras revisar los 2 modelos).

Reglas (para cuando se implemente): `chat_whatsapp_id` y `lead_id` inmutables tras crear;
solo un chat activo por lead; consultas ORDER BY created_at DESC LIMIT 1. El índice
compuesto (lead_id, created_at) soporta esa consulta.
"""

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


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
