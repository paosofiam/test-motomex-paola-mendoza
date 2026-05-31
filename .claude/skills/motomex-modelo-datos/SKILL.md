---
name: motomex-modelo-datos
description: Usar al crear o modificar la CAPA DE DATOS del backend Motomex (API-server) — modelos SQLAlchemy, schemas Pydantic, migraciones Alembic o seeders para cualquier tabla (productos, leads, chats, pre_ordenes, catálogos o tablas de relación). Garantiza columnas estándar, FKs `_id`, dinero en centavos, soft delete, índices/constraints UNIQUE y la matriz de métodos permitidos definidos en API-server/specs.
---

# Capa de datos Motomex (modelos · migraciones · seeders)

Esta skill asegura que cualquier modelo SQLAlchemy + schema Pydantic + migración + seeder cumpla las specs. **Lee primero** `API-server/specs/er_diagram.md` (estructura de la tabla en cuestión) y `API-server/specs/contracts.md` (matriz de métodos y por qués). Las decisiones canónicas que resuelven inconsistencias están en `API-server/CLAUDE.md`.

## Antes de escribir código

1. Identifica la tabla en `er_diagram.md` (columnas de dominio + FKs).
2. Confirma a qué **Tier** pertenece (define cómo viaja en la API, pero también si admite delete).
3. Busca su fila en la **matriz de métodos** de `contracts.md` / `API-server/CLAUDE.md`. **No implementes métodos fuera de esa fila.**
4. Decide nombres: archivo `*_model.py`, clase `*Model` en español (`ProductoModel`, `LeadModel`, …).

## Reglas no negociables

### Columnas estándar (TODAS las tablas, incluidas las de relación)
`id` PK autoincrement · `created_at` NOT NULL · `updated_at` NOT NULL · `deleted_at` NULL.
Centraliza estas 4 en un **mixin** reusable, p. ej. `app/core/mixins.py`:

```python
from datetime import datetime, timezone
from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

def _now() -> datetime:
    return datetime.now(timezone.utc)

class TimestampMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
```

- `create` ⇒ `created_at == updated_at` (mismo timestamp exacto). Si usas defaults separados, captura `ts = _now()` una vez y asígnalo a ambos para garantizar igualdad.
- `update` ⇒ refresca **solo** `updated_at`.
- `delete` ⇒ **soft delete**: set `deleted_at = _now()`. **Nunca** `session.delete()` (hard delete) en ninguna tabla.

### FKs con sufijo `_id`
Storage: `marca_id`, `moneda_id`, `ciudad_id`, `estado_id`, `intencion_de_compra_id`, `chat_status_id`, `lead_id`, `producto_id`, `vehiculo_id`, `categoria_id`, `pre_orden_id`. El nombre sin sufijo es solo contrato de respuesta.

### Dinero = `int` centavos
`productos.precio`, `monedas.tipo_de_cambio`, `pre_ordenes.total` ⇒ `Integer`. Nunca `Float`/`Numeric`. La conversión a MXN es responsabilidad de la capa API (no de la BD), salvo `pre_ordenes.total` que se **persiste ya convertido a MXN**.

### Catálogos sin delete
`marcas`, `monedas`, `ciudades`, `estados`, `vehiculos`, `categorias`, `intenciones_de_compra_de_leads`, `chat_statuses` **no** llevan método `delete` ni en modelo ni en API. Crecen solo por find-or-create.

### Constraints / índices (en la migración)
- UNIQUE natural normalizado: `marcas.marca`, `categorias.categoria`, `ciudades.ciudad`, `estados.estado`, `monedas.abreviacion`.
- UNIQUE compuesto `vehiculos (modelo, marca_id, anio)`.
- Índices `leads.chat_whatsapp_id`, `chats.chat_whatsapp_id`; índice compuesto `chats (lead_id, created_at)`.
- UNIQUE `(fk1, fk2)` en cada tabla de relación.
- `pre_ordenes_productos` añade `cantidad: Integer NOT NULL` además de las 2 FKs.

## Esqueleto de modelo

```python
# app/models/producto_model.py
from sqlalchemy import Integer, String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.core.mixins import TimestampMixin

class ProductoModel(TimestampMixin, Base):
    __tablename__ = "productos"

    marca_id: Mapped[int] = mapped_column(ForeignKey("marcas.id"), nullable=False)
    modelo: Mapped[str] = mapped_column(String(255), nullable=False)
    precio: Mapped[int] = mapped_column(Integer, nullable=False)          # centavos
    moneda_id: Mapped[int] = mapped_column(ForeignKey("monedas.id"), nullable=False, default=1)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    especificaciones: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Solo los métodos de la matriz: get_all, get_by_id, search, create, delete.
    # NO agregar update a ProductoModel.
```

Reglas de query en los métodos:
- Todo `get_*`/`search` filtra `deleted_at IS NULL`.
- `ChatModel.get_by_lead` y `get_by_chat_whatsapp_id`: `ORDER BY created_at DESC LIMIT 1` (un solo chat activo).
- Campos derivados (`leads.estado`, `leads.chat_id`) **no** son columnas: se resuelven por join en la capa de respuesta, no se almacenan.

## Migraciones (Alembic)

- La BD `motomex` debe existir en phpMyAdmin antes de migrar (`utf8mb4_unicode_ci`).
- Una migración por tabla siguiendo las fases de `contracts.md` (modelos uno por uno → migración → seeder).
- Incluye en cada `create_table` las 4 columnas estándar + FKs `_id` + índices/UNIQUE de arriba.
- Comandos (venv activo, desde `API-server/`): `alembic revision --autogenerate -m "..."` luego `alembic upgrade head`.

## Seeders

Datos **obligatorios y exactos** (de `er_diagram.md` → "Valores por defecto"):
- `monedas`: (1, Pesos Mexicanos, MXN, 100) · (2, Dólares, USD, 1700) · (3, Euros, EUR, 2300).
- `intenciones_de_compra_de_leads`: 1 baja · 2 media · 3 alta · 4 completa.
- `chat_statuses`: 1 activo · 2 en revisión · 3 en espera · 4 con cliente · 5 cerrado.

Datos de ejemplo (aleatorios, solo referencia): `categorias` (baterías, balatas…), `ciudades` (Monterrey/Nuevo León…), `vehiculos` (Versa, Sentra…), `marcas` (Nissan, Hyundai, Honda, BYD, Tesla). Inserta catálogos Tier 2 con el valor **ya normalizado** (lowercase, trim, sin acentos) para respetar el UNIQUE.

## Checklist antes de terminar
- [ ] 4 columnas estándar presentes (vía mixin).
- [ ] FKs con `_id`; tipos `int` para dinero.
- [ ] Solo métodos de la matriz; `create` setea ambos timestamps iguales; `delete` es soft.
- [ ] Índices/UNIQUE creados; catálogos sin `delete`.
- [ ] Seeders de monedas/intenciones/chat_statuses con ids exactos.
