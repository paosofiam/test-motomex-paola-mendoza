---
name: motomex-tests
description: Usar al crear o modificar PRUEBAS del backend Motomex (API-server) — tests pytest de modelos, schemas, controladores/endpoints, migraciones o seeders, o cuando se pida "agregar tests", "pruebas", "cobertura", "probar el endpoint X". Stack de pruebas SÍNCRONO (pytest + FastAPI TestClient, sin async, sin auth). Verifica los invariantes de specs: dinero en centavos/MXN, soft delete, columnas estándar, matriz de métodos, Tier 1/2/3, find-or-create/find-or-fail, RFC 7807 y reglas de chats/leads.
---

# Capa de pruebas Motomex (pytest · TestClient)

Esta skill asegura que las pruebas del backend ejerciten y **bloqueen regresiones** de los invariantes de `API-server/specs/` (`contracts.md`, `er_diagram.md`, `endpoints.md`) y las decisiones canónicas de `API-server/CLAUDE.md`. No introduce reglas nuevas: traduce a aserciones lo que las otras skills ya exigen (ver [[motomex-modelo-datos]], [[motomex-controlador-api]], [[motomex-revision-cumplimiento]]).

> **Coherencia de stack (no negociable).** El backend es **síncrono** (SQLAlchemy + PyMySQL, sin `async`/`await`, sin JWT/OAuth2). Las pruebas también: **`pytest` + `fastapi.testclient.TestClient`**. **NO** uses `pytest-asyncio`, `anyio`, `AsyncClient`, ni mocks de auth. Gestor de paquetes: **`pip`** (nunca `uv`).

## Antes de escribir un test

1. Identifica qué se prueba: modelo/seeder (capa datos), o endpoint (capa API).
2. Localiza el contrato: fila de la tabla de `endpoints.md` (status, body, Tier) o de la matriz de métodos (`API-server/CLAUDE.md`).
3. Lista los **invariantes** que tocan ese código (ver "Qué probar") y escribe una aserción por cada uno.
4. Nombre del archivo: `test_<recurso>_<capa>.py` (`test_producto_endpoints.py`, `test_chat_model.py`). Funciones `test_<comportamiento>` con verbo en inglés.

## Dependencias de prueba (no contaminar producción)

`pytest` y `httpx` (lo requiere `TestClient`) **no** están en `requirements.txt` y **no** deben agregarse ahí. Crea `API-server/requirements-dev.txt`:

```
-r requirements.txt
pytest>=8.3
httpx>=0.27
```

Instala (venv activo, desde `API-server/`): `pip install -r requirements-dev.txt`.

Config en `API-server/pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -ra
```

## Base de datos de pruebas

**Nunca** corras tests contra la BD `motomex` real (los escribirías/ensuciarías). Dos opciones, en orden de preferencia:

1. **MySQL dedicada `motomex_test`** (fidelidad total: JSON, UNIQUE normalizado, autoincrement como en prod). Créala una vez en phpMyAdmin (`utf8mb4_unicode_ci`) y expón `TEST_DATABASE_URL` en tu entorno (no en `.env`, que es deny). El `conftest` construye un engine propio y aísla cada test por rollback.
2. **SQLite en memoria** (rápido, sin XAMPP) **solo** si documentas las salvedades: el tipo `JSON`, algunos comportamientos de `UNIQUE`/colación y el `DateTime` no son idénticos a MySQL; no valida fidelidad de migraciones. Útil para tests de lógica pura, no para los de constraints.

Aislamiento por test: transacción + savepoint con rollback al final (cada test parte de BD limpia, sin hard-delete).

### `tests/conftest.py` (esqueleto)

```python
import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

TEST_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")
engine = create_engine(TEST_URL, future=True)

@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.create_all(engine)   # o aplica migraciones Alembic si pruebas fidelidad
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db():
    """Una transacción por test; rollback al final → sin residuos, sin hard delete."""
    conn = engine.connect()
    trans = conn.begin()
    session = Session(bind=conn, future=True)
    nested = conn.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart(sess, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = conn.begin_nested()

    yield session
    session.close()
    trans.rollback()
    conn.close()

@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

## Qué probar (invariante → aserción)

Cada invariante de las specs debe tener al menos un test que falle si se rompe.

### Dinero y conversión MXN
- `GET /productos` y `GET /productos/{id}`: `precio` es `int` (centavos) y **ya en MXN**. Para un producto con `moneda_id=2` (USD, `tipo_de_cambio=1700`), `precio_respuesta == round(precio_bd * 1700 / 100)`. Nunca `float` en el JSON.
- `pre_ordenes.total` devuelto es `int` y coincide con la suma convertida a MXN.

### Soft delete
- `DELETE /productos/{id}` → `204` sin body; luego `GET /productos/{id}` → `404` y la fila sigue en BD con `deleted_at IS NOT NULL`.
- Toda lista (`GET /productos`, `GET /leads`) **excluye** filas con `deleted_at`.
- Catálogos sin endpoint de delete: no existe ruta `DELETE` para `marcas`/`monedas`/etc.

### Columnas estándar y timestamps
- Tras `create`: `created_at == updated_at`. Tras `update` (PATCH): `updated_at > created_at`.
- Las 4 columnas existen en cada tabla nueva (test de capa datos sobre el modelo/migración).

### Matriz de métodos (lo que NO debe existir)
- `ProductoModel` no expone `update` (no hay `PATCH /productos`): petición a un PATCH inexistente → `405`/`404`.
- `ChatStatusModel` sin `create`; `PreOrdenModel` solo `create`. Verifica que no haya endpoints fuera de la tabla de `endpoints.md`.

### Tier 1/2/3
- Tier 1: `POST /productos` recibe `moneda_id` (int); la respuesta trae `"moneda": "MXN"` (string), no el id.
- Tier 2: `marca`/`categorias`/`ciudades` viajan como string en ambos sentidos. Normalización: enviar `"  NISSÁN "` resuelve al mismo registro que `"nissan"` (lowercase + trim + unidecode) y **no** crea duplicado.
- Tier 3: identificación por `id`; respuestas incluyen campos legibles.

### find-or-create vs find-or-fail
- `POST /productos` con `marca` inexistente → la crea (find-or-create), `201`. Vehículo nuevo con marca nueva → cascada crea ambos.
- `POST /leads` con `vehiculo` nuevo → find-or-create; con `ciudad` inexistente (find-or-fail) → `422` problem+json con `field` + `value_received`.
- `leads.productos_interes[]` por `modelo`: si matchea varios productos, se persisten **todas** las relaciones (cuenta filas en `leads_productos`).
- `pre_ordenes.productos[].producto_id` con id inexistente → `422`/`404`; **no** resuelve por string.

### RFC 7807
- Cualquier `4xx`/`5xx`: `Content-Type` empieza con `application/problem+json` y el body trae `type/title/status/detail/instance`; en validación, además `field` y `value_received`.

### Reglas de chats / leads
- `POST /chats` cuando el lead ya tiene chat activo → el previo queda con `deleted_at` y solo hay **uno** activo.
- `GET /chats?chat_whatsapp_id=` y `GET /chats/{id}` → un **solo** chat (el más reciente).
- `PATCH /chats/{id}` solo cambia `chat_status_id`/`resumen`; intentar mutar `lead_id`/`chat_whatsapp_id` no los cambia.
- `GET /leads`: respuesta incluye `chat_id` (chat activo) y `estado` derivado (`ciudad→estados`); el body de POST/PATCH **rechaza** `estado`.

### Seeders
- Tras seeding: `monedas` ids 1/2/3 con `tipo_de_cambio` 100/1700/2300; `intenciones` 1–4; `chat_statuses` 1–5 (valores exactos de `er_diagram.md`).

## Cómo correr

Desde `API-server/` con venv activo (usa `python -m pytest`, ya permitido por `settings.json`):

```powershell
python -m pytest                 # todo
python -m pytest tests/test_producto_endpoints.py -q
python -m pytest -k soft_delete  # por nombre
```

(Opcional: para escribir `pytest` a secas, añade `PowerShell(pytest*)` al allowlist de `.claude/settings.json` — pídelo y lo agrego con la skill `update-config`.)

## Patrón de un test de endpoint

```python
def test_delete_producto_es_soft(client, db):
    creado = client.post("/productos", json={
        "marca": "Nissan", "modelo": "Versa", "precio": 12999, "moneda_id": 1,
        "stock": 3, "especificaciones": {}, "vehiculos": [], "categorias": [], "ciudades": [],
    })
    assert creado.status_code == 201
    assert creado.headers["location"] == f"/productos/{creado.json()['id']}"
    pid = creado.json()["id"]

    assert client.delete(f"/productos/{pid}").status_code == 204
    r = client.get(f"/productos/{pid}")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    # la fila sigue existiendo, solo marcada:
    from app.models.producto_model import ProductoModel
    fila = db.get(ProductoModel, pid)
    assert fila is not None and fila.deleted_at is not None
```

## Checklist antes de terminar
- [ ] Tests **síncronos** (TestClient); sin `async`/`pytest-asyncio`/`AsyncClient`.
- [ ] Corren contra `motomex_test`/SQLite, **nunca** contra `motomex` real; aislamiento por rollback.
- [ ] `pytest`/`httpx` en `requirements-dev.txt`, no en `requirements.txt`.
- [ ] Cada invariante tocado tiene su aserción (dinero MXN/int, soft delete, timestamps, matriz, Tier, find-or-*, RFC 7807, chats/leads, seeders).
- [ ] Sin métodos/endpoints fuera de la matriz; sin hard delete en setup/teardown.
- [ ] No se leyó ni tocó `.env`; `TEST_DATABASE_URL` viene del entorno.
