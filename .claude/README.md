# .claude — Guardarraíles del proyecto Motomex

Configuración de Claude Code que asegura que toda implementación del backend respete `API-server/specs/`.

## Qué hay aquí

- **`settings.json`** — allowlist de comandos de desarrollo seguros (venv, pip, uvicorn, alembic, git de solo lectura) para reducir prompts de permiso; deny de lectura de `.env`.
- **`skills/`** — capacidades invocadas por Claude según la tarea:
  - `motomex-modelo-datos` — crear/editar modelos SQLAlchemy, migraciones Alembic y seeders (columnas estándar, FKs `_id`, dinero en centavos, soft delete, matriz de métodos, índices/UNIQUE).
  - `motomex-controlador-api` — crear/editar controladores/routers FastAPI y schemas (REST sin wrapper, RFC 7807, `Location`, conversión MXN, Tier 1/2/3, find-or-create/find-or-fail).
  - `motomex-revision-cumplimiento` — auditar el diff contra las specs antes de commit/PR.
  - `motomex-tests` — crear/editar pruebas pytest (stack síncrono: `TestClient`, sin async/auth) que verifican los invariantes de specs: dinero MXN/centavos, soft delete, columnas estándar, matriz de métodos, Tier 1/2/3, find-or-create/find-or-fail, RFC 7807 y reglas de chats/leads.

## Reglas ("rules")

Las reglas vinculantes viven como **CLAUDE.md anidados** (se auto-cargan):
- `CLAUDE.md` (raíz) — qué es el proyecto + invariantes transversales.
- `API-server/CLAUDE.md` — decisiones canónicas que resuelven las inconsistencias abiertas en "Observaciones de revisión" de `er_diagram.md`, matriz de métodos y clasificación Tier.

La **fuente de verdad** sigue siendo `API-server/specs/`. Estos archivos la destilan y resuelven ambigüedades; ante conflicto, manda la spec salvo donde `API-server/CLAUDE.md` declara una decisión explícita.
