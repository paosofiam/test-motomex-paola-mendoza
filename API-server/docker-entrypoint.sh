#!/bin/sh
set -e

echo "[entrypoint] Aplicando migraciones de base de datos (alembic upgrade head)..."
alembic upgrade head

echo "[entrypoint] Iniciando el servidor: $@"
exec "$@"
