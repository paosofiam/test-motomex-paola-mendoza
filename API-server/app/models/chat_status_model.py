"""Catálogo Tier 1: chat_statuses — TABLA ORM. Sin delete (catálogo estático, solo seeder).

El modelo solo expone `get_by_id`.
"""

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class ChatStatusModel(TimestampMixin, Base):
    __tablename__ = "chat_statuses"

    status: Mapped[str] = mapped_column(String(50), nullable=False)

    @classmethod
    def get_by_id(cls, db: Session, status_id: int) -> "ChatStatusModel | None":
        return db.scalar(select(cls).where(cls.id == status_id, cls.deleted_at.is_(None)))
