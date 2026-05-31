# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Technical test for an "AI & Automation Specialist" role at Motomex. The goal is an AI WhatsApp chatbot (built in **n8n**) that sells auto parts, recommends compatible products, and closes sales unattended. This repo currently contains only the **backend API** (`API-server/`) that the n8n chatbot will consume. The chatbot's consumer is an LLM agent — most API design decisions optimize for LLM token use and round-trips.

## Commands

All commands run from `API-server/` in PowerShell (Windows, Python 3.14 via `py -3.14`):

```powershell
# First-time setup
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env        # then edit if MySQL creds differ from root@localhost:3306

# Run the dev server (venv active)
uvicorn app.main:app --reload      # http://localhost:8000  (/docs, /redoc, /health)
```

Requires **XAMPP** running with MySQL + Apache. The API talks to the *same* MySQL instance as phpMyAdmin, so writes are mutually visible. The `motomex` database (collation `utf8mb4_unicode_ci`) must be created manually in phpMyAdmin before migrations.

No test suite or linter is configured yet. `requirements.txt` includes `alembic` (migrations) and `unidecode` (accent-stripping for the Tier 2 normalization described below); both are unused so far.

## Specs are the source of truth

The full design lives in `API-server/specs/` and **must be consulted before implementing models, migrations, or endpoints** — the actual code is currently only a scaffold (FastAPI app with a `/health` endpoint, settings, DB session factory; `models/`, `controllers/`, `core/`, `migrations/`, `seeders/` are empty placeholders). The three spec files cross-reference each other:

- **`contracts.md`** — stack, naming conventions, development phases, the model→method matrix, and the *business-logic rationale* ("por qués") behind the DB and endpoints.
- **`er_diagram.md`** — Mermaid ER diagram, every table/column/FK, the standard columns, seed/default data, and a "Observaciones de revisión" section listing known spec inconsistencies left for the implementer to resolve.
- **`endpoints.md`** — REST endpoint table, response/error formats, and the Tier 1/2/3 + find-or-create/find-or-fail policies.

Specs and the README are written in Spanish; domain vocabulary stays Spanish in code too (see conventions). Note: the root `README.md` links to specs as `./contracts.md` etc., but they actually live in `API-server/specs/`.

## Architecture & cross-cutting rules

FastAPI in an MVC-inspired layout: **Models** = SQLAlchemy ORM + Pydantic validation; **Controllers** = FastAPI routers with decorator-based exception handling and HTTP-status/response shaping; **Views** = the WhatsApp chat driven by the n8n bot. `app/database.py` exposes `engine`, `SessionLocal`, `Base` (a `DeclarativeBase`), and the `get_db()` dependency. `app/config.py` loads `.env` via pydantic-settings.

These rules span the whole data layer and endpoint surface — violating them in one place breaks the contract elsewhere:

- **Money is stored as `int` cents**, everywhere and in API responses too (`productos.precio`, `monedas.tipo_de_cambio`, `pre_ordenes.total`). `12999` = $129.99. The API consumer formats to decimal; never use floats. API responses always convert prices to **MXN** via `tipo_de_cambio` regardless of the product's original currency.
- **Soft delete only.** Every `delete` sets `deleted_at`; a row is active iff `deleted_at IS NULL`. Never hard-delete. Catalog tables (`marcas`, `monedas`, `ciudades`, `estados`, `vehiculos`, `categorias`, `intenciones_de_compra_de_leads`, `chat_statuses`) admit *no* delete at all — they are system constants, grown only via find-or-create.
- **Standard columns on every table** (including relation tables): `id` PK, `created_at`, `updated_at` (both set to the same timestamp on create), `deleted_at` nullable.
- **One active chat per lead.** `leads → chats` is 1:N relationally, but queries by `chat_whatsapp_id` or `lead_id` return at most one row (`created_at DESC LIMIT 1`, `deleted_at IS NULL`). Creating a new chat requires soft-deleting the prior one. `chat_whatsapp_id` (on leads and chats) is immutable after creation and must be indexed.
- **Tier 1/2/3 catalog policy** (in `endpoints.md`): Tier 1 (small/static: `monedas`, `chat_statuses`, `intenciones_de_compra_de_leads`, `estados`) → bodies send `*_id`, responses return the string. Tier 2 (`marcas`, `categorias`, `ciudades`, `vehiculos`) → strings both ways, API resolves to FK with deterministic normalization (lowercase, trim, unaccent). Tier 3 (`productos`, `leads`, `chats`, `pre_ordenes`) → identified by `id`, responses also include human-readable fields.
- **find-or-create vs find-or-fail.** `POST /productos` and the `vehiculo` field of `/leads` use find-or-create (catalog capture must be fluid, with cascade onto `marca`). Everything else is strict find-or-fail → `422` if a string doesn't resolve. `leads.productos_interes[]` is find-or-fail by `modelo` (it's real inventory; if multiple products match, persist the relation to all matches). `pre_ordenes.productos[].producto_id` requires the exact `id` (no string resolution).
- **Vehicles always travel as `{modelo, marca, anio}` objects**, never an opaque id, in both requests and responses. Identity is the UNIQUE composite `(modelo, marca, anio)`.
- **`leads.estado` is derived, not stored** — resolved via `leads.ciudad → ciudades.estado → estados.estado`; accepted in responses only, never in bodies. Similarly `Lead.chat_id` in responses is the active chat's id (a join), not a column.
- **REST with no response wrapper**: success returns the resource directly; HTTP status is the sole success signal. Errors use **RFC 7807** Problem Details (`application/problem+json`) with `type/title/status/detail/instance` plus extras like `field`/`value_received`.

## Naming conventions (from `contracts.md`)

DB tables: `snake_case`, plural, Spanish without accents (`productos`, `pre_ordenes`). Columns: `snake_case`, Spanish for domain / English for technical (`marca`, `created_at`). Model files `*_model.py` → classes `*Model` (`ProductoModel`); controller files `*_controller.py` → classes `*Controller`; router instances `*_router`. Methods/vars `snake_case` with English verbs (`get_by_id`, `create`). Each model's *allowed* methods are fixed by the matrix in `contracts.md` — don't add methods (e.g. `ProductoModel` has no `update`) without checking that table.
