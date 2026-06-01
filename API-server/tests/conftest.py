"""Configuración de pruebas (capa de datos, síncrona).

Stack: pytest puro (sin TestClient en esta tanda: se prueban los métodos `@classmethod`
de los modelos directamente sobre una `Session`). NO async, NO auth, gestor `pip`.

Aislamiento: una transacción real por test + savepoint anidado con rollback al final, de modo
que cada test parte de una BD limpia sin hard-delete y los `db.flush()` de los `create` (y los
`db.commit()` del seeder) quedan revertidos al terminar.

BD de pruebas: `TEST_DATABASE_URL` del entorno (MySQL `motomex_test`). Nunca la BD `motomex`
real. Si no se exporta, cae a SQLite en memoria (útil solo para lógica pura; menor fidelidad).
"""

import os
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app as fastapi_app  # alias: `import app.models` re-vincularía el nombre `app`
import app.models  # noqa: F401  registra las 18 tablas en Base.metadata
from app.core.mixins import _now
from app.models.ciudad_model import CiudadModel
from app.models.estado_model import EstadoModel
from seeders import catalog_defaults

TEST_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")

if TEST_URL.startswith("sqlite"):
    # StaticPool + una sola conexión: necesario para que el esquema en memoria sea visible
    # entre `_schema` y cada test (de lo contrario cada connect() abriría una BD vacía nueva).
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


def _client(db, *, raise_server_exceptions=True):
    """`TestClient` sobre la misma sesión `db` del test (override de `get_db`).

    El endpoint comparte la transacción+savepoint del test, así que lo que escribe vía HTTP es
    visible en `db` para las aserciones y se revierte al final (sin tocar la BD real). El override
    devuelve la sesión directamente: NO ejecuta el `commit()/close()` de `get_db`, porque el
    aislamiento ya lo gestiona la fixture `db`.
    """
    fastapi_app.dependency_overrides[get_db] = lambda: db
    return TestClient(fastapi_app, raise_server_exceptions=raise_server_exceptions)


@pytest.fixture
def client(db):
    """`TestClient` que RE-LANZA excepciones no controladas (default): un 500 inesperado falla el test."""
    with _client(db) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def client_no_raise(db):
    """`TestClient` que NO re-lanza: devuelve la respuesta 500 real (RFC 7807) que vería el cliente.

    Necesario para observar el comportamiento de producción cuando una excepción no controlada
    (p. ej. `IntegrityError` de una FK no validada en el service) llega al handler genérico.
    """
    with _client(db, raise_server_exceptions=False) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def seed_catalogs(db):
    """Catálogos Tier 1 con ids exactos (vía seeder) + un estado y ciudad de apoyo.

    Devuelve los ids/strings que necesitan los tests de leads/productos/chats.
    """
    catalog_defaults.seed(db)  # monedas 1-3, intenciones 1-4, chat_statuses 1-5

    ts = _now()
    estado = EstadoModel(estado="Jalisco", created_at=ts, updated_at=ts)
    db.add(estado)
    db.flush()
    ciudad = CiudadModel.create(db, ciudad="Guadalajara", estado_id=estado.id)

    return SimpleNamespace(
        estado_id=estado.id,
        estado_nombre="Jalisco",
        ciudad_id=ciudad.id,
        ciudad_nombre="guadalajara",  # ya normalizado
        moneda_mxn_id=1,
        moneda_usd_id=2,
        moneda_eur_id=3,
        intencion_id=1,
        chat_status_id=1,
    )
