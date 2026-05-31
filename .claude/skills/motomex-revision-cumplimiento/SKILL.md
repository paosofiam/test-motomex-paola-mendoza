---
name: motomex-revision-cumplimiento
description: Usar para auditar/revisar que el código del backend Motomex (API-server) cumple las specs antes de commit, PR o entrega — o cuando se pida "revisar cumplimiento", "validar contra specs", "code review del backend". Verifica columnas estándar, dinero en centavos, soft delete, matriz de métodos, Tier 1/2/3, find-or-create/find-or-fail, RFC 7807, conversión MXN y reglas de chats/leads.
---

# Revisión de cumplimiento de specs — backend Motomex

Auditoría sistemática del código de `API-server/` contra `specs/` (`contracts.md`, `er_diagram.md`, `endpoints.md`) y las decisiones canónicas de `API-server/CLAUDE.md`. Úsala antes de cerrar cualquier cambio.

## Cómo revisar
1. Lee el diff (`git diff`) o los archivos tocados.
2. Recorre las secciones de checklist de abajo que apliquen a esos archivos.
3. Reporta cada incumplimiento como: **archivo:línea → regla violada → corrección**. Cita la spec (`endpoints.md §...`).
4. No apruebes si hay invariantes rotos (dinero float, hard delete, wrapper de respuesta, método fuera de matriz).

## Checklist — capa de datos (modelos/migraciones/seeders)
- [ ] 4 columnas estándar (`id`, `created_at`, `updated_at`, `deleted_at`) en **toda** tabla, incluidas las de relación.
- [ ] FKs nombradas `<entidad>_id`.
- [ ] Dinero (`precio`, `tipo_de_cambio`, `total`) es `Integer` (centavos). **Cero** `Float`/`Numeric`.
- [ ] `create` escribe `created_at == updated_at`; `update` refresca solo `updated_at`.
- [ ] `delete` es soft (`deleted_at`), **nunca** hard. Catálogos sin método `delete`.
- [ ] Métodos del modelo == fila de la matriz (ni más ni menos). `ProductoModel` sin `update`; `ChatStatusModel` sin `create`; `PreOrdenModel` solo `create`.
- [ ] UNIQUE: catálogos Tier 2 (valor normalizado), `vehiculos(modelo,marca_id,anio)`, `(fk1,fk2)` en relaciones.
- [ ] Índices: `leads.chat_whatsapp_id`, `chats.chat_whatsapp_id`, `chats(lead_id,created_at)`.
- [ ] `pre_ordenes_productos.cantidad` `int NOT NULL`.
- [ ] Seeders exactos: `monedas`(1 MXN 100 / 2 USD 1700 / 3 EUR 2300), `intenciones`(baja/media/alta/completa), `chat_statuses`(activo/en revisión/en espera/con cliente/cerrado).
- [ ] No existen columnas `leads.estado`, `leads.estado_id`, `leads.chat_id` (son derivados).

## Checklist — capa de API (controladores/routers/schemas)
- [ ] Respuestas sin wrapper; arrays planos; status de la tabla de `endpoints.md`.
- [ ] POST ⇒ `201` + `Location`; PATCH ⇒ `200` + recurso completo; DELETE ⇒ `204` sin body.
- [ ] Errores `4xx`/`5xx` en `application/problem+json` con `type/title/status/detail/instance` (+ `field`/`value_received` en validación).
- [ ] Precios en respuestas convertidos a MXN (`round(precio*tipo_de_cambio/100)`), `int` centavos.
- [ ] Tier respetado: Tier 1 id→string; Tier 2 string↔string con normalización (lowercase/trim/unidecode) idéntica en find y create; Tier 3 por id + campos legibles; `productos_interes` como `[string]`.
- [ ] find-or-create solo en: `POST /productos` (marca, vehiculos, categorias, ciudades) y `vehiculo` de `/leads` (cascada marca). Todo lo demás find-or-fail ⇒ `422` con `value_received`.
- [ ] `leads.productos_interes[]` find-or-fail por modelo, multi-match persiste todas las relaciones.
- [ ] `pre_ordenes.productos[].producto_id` exige id exacto (sin resolución por string).
- [ ] Vehículos siempre `{modelo, marca, anio}` en request y response.
- [ ] `GET /chats*` devuelve un solo chat (más reciente); `POST /chats` soft-deletea el chat activo previo.
- [ ] `PATCH /chats/{id}` solo `chat_status_id`/`resumen`; `lead_id`/`chat_whatsapp_id` inmutables.
- [ ] `/leads` response incluye `chat_id` y `estado` derivados; body **no** acepta `estado`.
- [ ] `telefono` valida E.164 (≤15 chars, prefijo `+`).
- [ ] **Toda** query filtra `deleted_at IS NULL`.

## Checklist — convenciones y estructura
- [ ] Archivos/clases: `*_model.py`→`*Model`, `*_controller.py`→`*Controller`, `*_router`; dominio en español.
- [ ] Reusa `Base`/`SessionLocal`/`get_db` de `app/database.py`; settings de `app/config.py`.
- [ ] No se tocó `.env` (solo `.env.example`). Sin secretos hardcodeados.

## Señales de alarma (rechazo inmediato)
- `float`/`Numeric` para dinero · `session.delete(...)` (hard delete) · wrapper `{"data":...}` · método fuera de la matriz · `HTTPException` crudo sin problem+json · query sin filtro `deleted_at IS NULL` · `estado`/`chat_id` como columna de `leads`.
