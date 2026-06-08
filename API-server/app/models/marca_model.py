"""Catálogo Tier 2: marcas — TABLA ORM. Crece solo por find-or-create.

El valor `marca` se almacena ya normalizado (lowercase/trim/sin acentos) y es UNIQUE. La creación
con normalización vive en `core/resolvers.find_or_create_marca`; el modelo solo expone `get_by_id`.
"""

from sqlalchemy import String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class MarcaModel(TimestampMixin, Base):
    __tablename__ = "marcas"
    __table_args__ = (UniqueConstraint("marca", name="uq_marcas_marca"),)

    marca: Mapped[str] = mapped_column(String(255), nullable=False)

    @classmethod
    def get_by_id(cls, db: Session, marca_id: int) -> "MarcaModel | None":
        return db.scalar(select(cls).where(cls.id == marca_id, cls.deleted_at.is_(None)))
