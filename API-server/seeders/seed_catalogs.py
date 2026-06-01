"""Siembra SOLO los catálogos constantes del sistema (Tier 1).

Uso (venv activo, desde API-server/):  python -m seeders.seed_catalogs

Inserta monedas, intenciones_de_compra_de_leads y chat_statuses con sus ids exactos.
NO inserta datos de ejemplo (productos/leads/chats): el resto de las tablas se pueblan
por el flujo del chatbot. Idempotente: re-ejecutar no duplica filas, por lo que es seguro
correrlo en cada arranque del contenedor (lo hace docker-entrypoint.sh tras las migraciones).
"""

import app.models  # noqa: F401  -- registra todas las tablas/relaciones
from app.database import SessionLocal
from seeders import catalog_defaults


def main() -> None:
    db = SessionLocal()
    try:
        catalog_defaults.seed(db)
        print(">> Catálogos del sistema sembrados: monedas, intenciones_de_compra_de_leads, chat_statuses.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
