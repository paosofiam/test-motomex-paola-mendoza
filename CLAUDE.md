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

The full design lives in `API-server/specs/` and **must be consulted before implementing models, migrations, or endpoints**. The code is implemented in a **router → service → model** layout under `app/` (`routers/`, `services/`, `models/`, `schemas/`, `core/`) plus `seeders/` and `tests/`. There is **no** `controllers/` directory — the layer that links endpoints to models are the **services**. The three spec files cross-reference each other:

- **`contracts.md`** — stack, naming conventions, development phases, the model→method matrix, and the *business-logic rationale* ("por qués") behind the DB and endpoints.
- **`er_diagram.md`** — Mermaid ER diagram, every table/column/FK, the standard columns, seed/default data, and a "Observaciones de revisión" section listing known spec inconsistencies left for the implementer to resolve.
- **`endpoints.md`** — REST endpoint table, response/error formats, and the Tier 1/2/3 + find-or-create/find-or-fail policies.

Specs and the README are written in Spanish; domain vocabulary stays Spanish in code too (see conventions). Note: the root `README.md` links to specs as `./contracts.md` etc., but they actually live in `API-server/specs/`.

## Architecture & cross-cutting rules

FastAPI organized as **router → service → model** (not MVC; there is **no** controllers layer): **Models** = pure SQLAlchemy ORM table definitions (columns + relationships, at most `get_by_id`) — filtered queries, writes with logic, and multi-entity orchestration live in the **Services** (module-level functions taking a `Session`, delegating generic helpers/catalog resolution to `core/resolvers.py`), per standard FastAPI practice (data operations are Session-taking functions, not ORM-model methods); **Routers** = the HTTP boundary (FastAPI `APIRouter`s) that declare routes, validate request/response with Pydantic, set HTTP status and the `Location` header, and delegate RFC 7807 error translation to registered exception handlers; **Views** = the WhatsApp chat driven by the n8n bot. `app/database.py` exposes `engine`, `SessionLocal`, `Base` (a `DeclarativeBase`), and the `get_db()` dependency. `app/config.py` loads `.env` via pydantic-settings.

These rules span the whole data layer and endpoint surface — violating them in one place breaks the contract elsewhere:

- **Money is stored as `int` cents**, everywhere and in API responses too (`productos.precio`, `monedas.tipo_de_cambio`, `pre_ordenes.total`). `12999` = $129.99. The API consumer formats to decimal; never use floats. API responses always convert prices to **MXN** via `tipo_de_cambio` regardless of the product's original currency.
- **Soft delete only.** Every `delete` sets `deleted_at`; a row is active iff `deleted_at IS NULL`. Never hard-delete. Catalog tables (`marcas`, `monedas`, `ciudades`, `estados`, `vehiculos`, `categorias`, `intenciones_de_compra_de_leads`, `chat_statuses`) admit *no* delete at all — they are system constants, grown only via find-or-create.
- **Standard columns on every table** (including relation tables): `id` PK, `created_at`, `updated_at` (both set to the same timestamp on create), `deleted_at` nullable.
- **One active row per `chat_whatsapp_id` (leads and chats).** `leads → chats` is 1:N relationally, but queries by `chat_whatsapp_id` (or `lead_id`) return at most one row (`created_at DESC LIMIT 1`, `deleted_at IS NULL`). `POST` is **idempotent**: if an active row already exists (chats: same `lead_id` **or** `chat_whatsapp_id`; leads: same `chat_whatsapp_id`), it is returned with `200 OK` — nothing is created or deleted. `create` **never** soft-deletes the prior row: replacing a chat requires an explicit `DELETE` first; leads are never deleted via the API. `chat_whatsapp_id` (on leads and chats) is immutable after creation and must be indexed. Uniqueness is enforced in the service layer (MySQL has no partial UNIQUE on `deleted_at IS NULL`), leaving a small TOCTOU window under concurrency.
- **Tier 1/2/3 catalog policy** (in `endpoints.md`): Tier 1 (small/static: `monedas`, `chat_statuses`, `intenciones_de_compra_de_leads`, `estados`) → bodies send `*_id`, responses return the string. Tier 2 (`marcas`, `categorias`, `ciudades`, `vehiculos`) → strings both ways, API resolves to FK with deterministic normalization (lowercase, trim, unaccent). Tier 3 (`productos`, `leads`, `chats`, `pre_ordenes`) → identified by `id`, responses also include human-readable fields.
- **find-or-create vs find-or-fail vs find-or-skip.** `POST /productos` and the `vehiculo` field of `/leads` use find-or-create (catalog capture must be fluid, with cascade onto `marca`). Most other strings are strict find-or-fail → `422` if they don't resolve. **Exception:** `leads.productos_interes[]` is **find-or-skip additive** by `modelo` — `productos` is real inventory so a client mention never creates a product (not find-or-create), but a missing model never blocks the lead either (not find-or-fail): it's skipped with a `Warning` header (partial success, like cities) and the lead is created/updated anyway. If multiple products match a `modelo`, persist the relation to all matches. On `PATCH`, `productos_interes` and `vehiculo` link **additively** (combine with existing, never replace or delete; empty/omitted = no change; no removal via API). `pre_ordenes.productos[].producto_id` requires the exact `id` (no string resolution).
- **Vehicles always travel as `{modelo, marca, anio}` objects**, never an opaque id, in both requests and responses. Identity is the UNIQUE composite `(modelo, marca, anio)`.
- **`leads.estado` is derived, not stored** — resolved via `leads.ciudad → ciudades.estado → estados.estado`; accepted in responses only, never in bodies. Similarly `Lead.chat_id` and `Lead.status` in responses come from the active chat (a join via `resolvers.get_active_chat`), not columns. Both `Lead` and `Chat` also expose cross-reference aliases (`lead_id`/`chat_id`) equal to their own `id`, purely informational for the LLM consumer.
- **REST with no response wrapper**: success returns the resource directly; HTTP status is the sole success signal. Errors use **RFC 7807** Problem Details (`application/problem+json`) with `type/title/status/detail/instance` plus extras like `field`/`value_received`.

## Naming conventions (from `contracts.md`)

DB tables: `snake_case`, plural, Spanish without accents (`productos`, `pre_ordenes`). Columns: `snake_case`, Spanish for domain / English for technical (`marca`, `created_at`). Model files `*_model.py` → classes `*Model` (`ProductoModel`); router files are plural by resource (`productos.py`, `leads.py`) with a module-level `router = APIRouter(...)` instance (there are **no** `*_controller.py` files or `*Controller` classes). Service files `*_service.py` → module-level functions (no classes). Methods/vars `snake_case` with English verbs (`get_by_id`, `create`). Each model's *allowed* methods are fixed by the matrix in `contracts.md` — Tier 3 models (`productos`, `leads`, `chats`, `pre_ordenes`) are pure tables exposing at most `get_by_id`; their `search`/`create`/`update`/`delete` live in the matching `*_service.py`. Don't add methods to a model without checking that table.
