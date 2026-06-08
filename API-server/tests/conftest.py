"""Configuración de pruebas (capa de datos, síncrona).

Stack: pytest puro (sin TestClient en esta tanda: se prueban los métodos `@classmethod`
de los modelos directamente sobre una `Session`). NO async, NO auth, gestor `pip`.

Aislamiento: una transacción real por test + savepoint anidado con rollback al final, de modo
que cada test parte de una BD limpia sin hard-delete y los `db.flush()` de los `create` (y los
`db.commit()` del seeder) quedan revertidos al terminar.

BD de pruebas: `TEST_DATABASE_URL` del entorno (MySQL `motomex_test`). Nunca la BD `motomex`
real. Si no se exporta, cae a SQLite en memoria (útil solo para lógica pura; menor fidelidad).

`app.main.app` se importa con alias `as fastapi_app` porque `import app.models` re-vincularía el
nombre `app` al paquete; el alias preserva la referencia a la instancia FastAPI. Ese `import
app.models` (con `# noqa: F401`) registra las 18 tablas en `Base.metadata`.

Para SQLite en memoria se usa StaticPool con una sola conexión: necesario para que el esquema
creado en `_schema` sea visible en cada test (de lo contrario cada connect() abriría una BD vacía
nueva).
"""

import os
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.core import resolvers
from app.database import Base, get_db
from app.main import app as fastapi_app
import app.models  # noqa: F401
from app.models.estado_model import EstadoModel
from seeders import catalog_defaults, estados

TEST_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")

if TEST_URL.startswith("sqlite"):
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        TEST_URL, future=True, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
else:
    engine = create_engine(TEST_URL, future=True)


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.create_all(engine)
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
    """`TestClient` sobre la misma sesión `db` del test (override de `get_db`).

    El endpoint comparte la transacción+savepoint del test, así que lo que escribe vía HTTP es
    visible en `db` para las aserciones y se revierte al final (sin tocar la BD real). El override
    devuelve la sesión directamente: NO ejecuta el `commit()/close()` de `get_db`, porque el
    aislamiento ya lo gestiona la fixture `db`. Re-lanza excepciones no controladas (default), así
    un 500 inesperado falla el test de forma ruidosa.
    """
    fastapi_app.dependency_overrides[get_db] = lambda: db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def seed_catalogs(db):
    """Catálogos Tier 1 con ids exactos (vía seeder) + las 32 entidades y una ciudad de apoyo.

    Puebla monedas 1-3, intenciones 1-4, chat_statuses 1-5 y las 32 entidades federativas (con
    `abreviacion`, vía `seeders.estados`), de modo que los tests puedan resolver estados por nombre
    o abreviación y crear ciudades bajo cualquier estado. Crea la ciudad de apoyo "Guadalajara" bajo
    Jalisco. Devuelve los ids/strings que necesitan los tests; `ciudad_nombre` viaja ya normalizado.
    """
    catalog_defaults.seed(db)
    estados.seed(db)

    jalisco = db.scalar(select(EstadoModel).where(EstadoModel.estado == "Jalisco"))
    ciudad = resolvers.find_or_create_ciudad(db, "Guadalajara", jalisco.id)

    return SimpleNamespace(
        estado_id=jalisco.id,
        estado_nombre="Jalisco",
        estado_abreviacion="JAL",
        ciudad_id=ciudad.id,
        ciudad_nombre="guadalajara",
        moneda_mxn_id=1,
        moneda_usd_id=2,
        moneda_eur_id=3,
        intencion_id=1,
        chat_status_id=1,
    )
