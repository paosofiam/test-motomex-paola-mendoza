# Imagen base: Python 3.14 en su versión "slim" (ligera).
FROM python:3.14-slim

# Buenas prácticas: que Python no guarde cache ni bufferee la salida (logs en vivo).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Carpeta de trabajo dentro de la imagen.
WORKDIR /app

# 1) Instalar dependencias primero (acelera reconstrucciones futuras).
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 2) Copiar solo lo necesario para ejecutar (no tests, no specs, no .env).
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY seeders/ ./seeders/
COPY alembic.ini ./
COPY docker-entrypoint.sh ./

# Permisos del script de arranque y un usuario sin privilegios (más seguro).
RUN chmod +x docker-entrypoint.sh \
 && adduser --disabled-password --gecos "" appuser \
 && chown -R appuser /app
USER appuser

# El backend escucha en el puerto 8000.
EXPOSE 8000

# Chequeo de salud: Docker consulta /health para saber si el backend está sano.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

# Al arrancar: primero el script (aplica migraciones), luego el comando de abajo.
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
