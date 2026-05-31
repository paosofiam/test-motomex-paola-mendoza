"""Entidad Tier 3: pre_ordenes. Sin métodos (pendiente).

`total` se persiste en MXN ya convertido (centavos). NO lleva `moneda_id`.
"""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampMixin
from app.database import Base


class PreOrdenModel(TimestampMixin, Base):
    __tablename__ = "pre_ordenes"

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)  # centavos, MXN
