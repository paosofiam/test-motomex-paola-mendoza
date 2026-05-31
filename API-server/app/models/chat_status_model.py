"""Catálogo Tier 1: chat_statuses. Sin métodos (pendiente). Sin delete (catálogo estático)."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class ChatStatusModel(TimestampMixin, Base):
    __tablename__ = "chat_statuses"

    status: Mapped[str] = mapped_column(String(50), nullable=False)
