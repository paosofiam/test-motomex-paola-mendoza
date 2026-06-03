"""Columnas estándar compartidas por TODAS las tablas (incl. tablas de relación).

Definición canónica de `er_diagram.md` → "Columnas estándar":
`id` PK · `created_at` NOT NULL · `updated_at` NOT NULL · `deleted_at` NULL.

`create` ⇒ `created_at == updated_at` (mismo timestamp exacto).
`update` ⇒ refresca solo `updated_at`.
`delete` ⇒ soft delete: set `deleted_at = _now()`. Nunca hard delete.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column


def _now() -> datetime:
    """Timestamp único (UTC) para asignar a created_at/updated_at/deleted_at."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Mixin de columnas estándar (`id`, `created_at`, `updated_at`, `deleted_at`).

    `created_at` lleva `default=_now` como fallback de conveniencia; `updated_at` NO lleva default
    y debe asignarse con el MISMO `ts = _now()` que `created_at` para garantizar
    `created_at == updated_at` en el INSERT (contrato de modelo). Si ambas columnas usaran
    `default=_now`, SQLAlchemy llamaría `_now()` en momentos distintos → `created_at != updated_at`
    en la base de datos, violando la invariante silenciosamente.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
