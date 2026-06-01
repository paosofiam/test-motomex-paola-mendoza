#!/bin/sh
set -e

echo "[entrypoint] Aplicando migraciones de base de datos (alembic upgrade head)..."
alembic upgrade head

# Siembra SOLO los catalogos constantes del sistema (Tier 1: monedas,
# intenciones_de_compra_de_leads, chat_statuses). La app los necesita siempre.
# Corre DENTRO del contenedor con el mismo DATABASE_URL que usa la app, asi que
# siempre siembra la base de datos que la app realmente usa (la "indicada"), y es
# idempotente -> seguro de re-correr en cada arranque. NO siembra datos de ejemplo;
# el resto de las tablas se pueblan por el flujo del chatbot.
echo "[entrypoint] Sembrando catalogos del sistema..."
python -m seeders.seed_catalogs

echo "[entrypoint] Iniciando el servidor: $@"
exec "$@"
