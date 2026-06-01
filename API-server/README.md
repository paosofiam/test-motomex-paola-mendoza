# Motomex API

Backend REST en **FastAPI** para el chatbot de WhatsApp de Motomex. El consumidor principal es un agente LLM (n8n), por lo que las decisiones de diseño priorizan minimizar tokens y roundtrips.

- Base de datos: MySQL (XAMPP local, misma instancia que phpMyAdmin)
- Arquitectura de capas: **router → service → model**
- Documentación interactiva: `/docs` (Swagger UI) y `/redoc`

---

## Requisitos previos

- **Python 3.14** instalado y disponible vía `py -3.14` (Windows Python Launcher).
- **XAMPP** corriendo con **MySQL** y **Apache** activos.
- Base de datos `motomex` creada manualmente en phpMyAdmin con collation `utf8mb4_unicode_ci`.
- (Opcional) phpMyAdmin en `http://localhost/phpmyadmin` para inspeccionar la BD.

---

## Configuración inicial (primera vez)

Desde `API-server/` en PowerShell:

```powershell
# 1. Crear entorno virtual
py -3.14 -m venv .venv

# 2. Activarlo
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear archivo de variables de entorno
Copy-Item .env.example .env
```

Edita `.env` si tus credenciales de MySQL difieren del default (`root` sin contraseña en `localhost:3306`). El `.env` no se versiona.

### Migraciones y seed

```powershell
# Aplicar migraciones (crea/actualiza tablas)
alembic upgrade head

# Poblar catálogos estáticos (chat_statuses, intenciones_de_compra, etc.)
python -m seeders.run_all
```

---

## Iniciar el servidor

Con el venv activo y **desde `API-server/`**:

```powershell
uvicorn app.main:app --reload
```

> **Importante:** el `.env` se carga con ruta relativa al directorio de trabajo. Correr `uvicorn` desde otro directorio hace que la app no encuentre el `.env` y falle con un error engañoso de credenciales MySQL.

El servidor queda disponible en:

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/health` | Healthcheck → `{"status": "ok"}` |
| `http://localhost:8000/docs` | Swagger UI interactivo |
| `http://localhost:8000/redoc` | Documentación ReDoc |

---

## Ejecutar los tests

Los tests requieren una base de datos separada `motomex_test`. Créala en phpMyAdmin antes de correr los tests.

```powershell
# Desde API-server/, con el venv activo
$env:TEST_DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3307/motomex_test"
pytest
```

La suite usa MySQL real (no mocks). El `conftest.py` crea y destruye las tablas automáticamente en cada sesión.

Para correr un subconjunto específico:

```powershell
pytest tests/models/          # solo tests de modelos
pytest tests/api/             # solo tests de endpoints
pytest tests/services/        # solo tests de servicios
pytest -v                     # con output detallado
```

---

## Endpoints

### Productos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/productos` | Lista productos. Query params opcionales: `marca`, `precio_minimo` |
| `POST` | `/productos` | Crea producto. Find-or-create para `marca`, `vehiculos`, `categorias` |
| `GET` | `/productos/{id}` | Obtiene producto por id |
| `DELETE` | `/productos/{id}` | Soft-delete de producto |

**Body `POST /productos`:**
```json
{
  "marca": "string",
  "modelo": "string",
  "precio": 12999,
  "moneda_id": 1,
  "stock": 10,
  "especificaciones": { "campo": "valor" },
  "vehiculos": [{ "modelo": "string", "marca": "string", "anio": 2020 }],
  "categorias": ["string"],
  "ciudades": ["string"]
}
```

**Respuesta `Producto`:**
```json
{
  "id": 1,
  "marca": "string",
  "modelo": "string",
  "precio": 12999,
  "moneda": "MXN",
  "stock": 10,
  "especificaciones": {}
}
```

> `precio` se devuelve **siempre en MXN** (centavos), independientemente de la moneda de origen.

---

### Leads

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/leads` | Lista leads. Query params: `chat_whatsapp_id`, `intencion_de_compra` |
| `POST` | `/leads` | Crea lead |
| `GET` | `/leads/{id}` | Obtiene lead por id |
| `PATCH` | `/leads/{id}` | Actualiza lead (retorna recurso completo) |

**Body `POST /leads`:**
```json
{
  "chat_whatsapp_id": "string",
  "nombre_whatsapp": "string",
  "telefono": "+521234567890",
  "nombre": "string",
  "ciudad": "string",
  "productos_interes": ["modelo_producto"],
  "vehiculo": [{ "modelo": "string", "marca": "string", "anio": 2020 }],
  "direccion_envio": "string",
  "intencion_de_compra_id": 1
}
```

> `estado` no se acepta en el body — se deriva automáticamente de `ciudad → ciudades.estado_id → estados.estado`.

---

### Chats

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/chats` | Obtiene chat activo. Query param: `chat_whatsapp_id` |
| `POST` | `/chats` | Crea chat (soft-delete del previo del mismo lead) |
| `GET` | `/chats/{id}` | Obtiene chat por id |
| `PATCH` | `/chats/{id}` | Actualiza `chat_status_id` y/o `resumen` |
| `DELETE` | `/chats/{id}` | Soft-delete de chat |

> Solo puede haber **un chat activo por lead**. Crear un nuevo chat soft-elimina el anterior automáticamente.

---

### Pre-órdenes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/pre_ordenes` | Crea pre-orden |

**Body `POST /pre_ordenes`:**
```json
{
  "lead_id": 1,
  "total": 25998,
  "productos": [{ "producto_id": 1, "cantidad": 2 }]
}
```

> `total` se persiste en MXN ya convertido (centavos). `producto_id` debe ser el id exacto — no hay resolución por string en pre-órdenes.

---

## Formato de respuestas

### Éxito

El body devuelve el recurso directamente, sin wrapper. El status HTTP es la única señal de éxito.

- `POST` → `201 Created` + header `Location: /<recurso>/{id}` + body con el recurso
- `PATCH` → `200 OK` + body con el recurso completo actualizado
- `DELETE` → `204 No Content` (sin body)

### Error — RFC 7807 Problem Details

Todos los errores `4xx`/`5xx` usan `Content-Type: application/problem+json`:

```json
{
  "type": "https://api.example.com/errors/unprocessable-entity",
  "title": "Validation failed",
  "status": 422,
  "detail": "El campo 'vehiculo[0].marca' no se pudo resolver",
  "field": "vehiculo[0].marca",
  "value_received": "Hiunday"
}
```

---

## Reglas de negocio clave

### Dinero siempre en centavos enteros
`precio`, `tipo_de_cambio` y `total` se almacenan como `int`. `12999` = $129.99. Nunca floats.

### Política de catálogos (Tier 1/2/3)

| Tier | Catálogos | Body petición | Body respuesta |
|------|-----------|---------------|----------------|
| **1** — pequeños/estáticos | `monedas`, `chat_statuses`, `intenciones_de_compra_de_leads`, `estados` | `*_id` (int) | string |
| **2** — medianos/dinámicos | `marcas`, `categorias`, `ciudades`, `vehiculos` | string | string |
| **3** — entidades dinámicas | `productos`, `leads`, `chats`, `pre_ordenes` | `id` (int) | objeto completo |

### Find-or-create vs find-or-fail

- **Find-or-create:** `marca` y `vehiculos` en `POST /productos`; `vehiculo` en `POST/PATCH /leads`. La captura conversacional puede crear entidades nuevas en cascada.
- **Find-or-fail:** todo lo demás. Si el string no resuelve, devuelve `422` con el campo y el valor recibido.
- `leads.productos_interes[]`: find-or-fail por `modelo`. Si el modelo coincide con varios productos, se persiste la relación con todos.

### Soft delete
Todo delete setea `deleted_at`; nunca hard-delete. Activo = `deleted_at IS NULL`. Los catálogos (`marcas`, `monedas`, `ciudades`, `estados`, `vehiculos`, `categorias`, `intenciones_de_compra_de_leads`, `chat_statuses`) no admiten delete de ningún tipo.

---

## Estructura del proyecto

```
API-server/
├── app/
│   ├── main.py                # Instancia FastAPI, registro de routers y handlers
│   ├── config.py              # Settings (pydantic-settings, carga .env)
│   ├── database.py            # engine, SessionLocal, Base, get_db()
│   ├── models/                # Modelos SQLAlchemy (una clase por archivo)
│   ├── schemas/               # Schemas Pydantic de request/response
│   ├── routers/               # Routers FastAPI (frontera HTTP)
│   ├── services/              # Lógica de negocio (sin dependencias HTTP)
│   └── core/
│       ├── exceptions.py      # Excepciones de dominio
│       ├── error_handlers.py  # Traducción de excepciones a RFC 7807
│       ├── normalization.py   # Normalización Tier 2 (lowercase, trim, unaccent)
│       ├── resolvers.py       # find-or-create / find-or-fail
│       └── mixins.py          # Columnas estándar (created_at, updated_at, deleted_at)
├── migrations/                # Migraciones Alembic
├── seeders/                   # Scripts de seed para catálogos estáticos
├── tests/
│   ├── conftest.py            # Fixtures de BD de test y cliente HTTP
│   ├── factories.py           # Factories de datos de test
│   ├── models/                # Tests de modelos SQLAlchemy
│   ├── services/              # Tests de services
│   └── api/                   # Tests de endpoints (integración)
├── specs/                     # Contratos y diagrama ER (fuente de verdad del diseño)
├── .env.example               # Plantilla de variables de entorno
├── requirements.txt
└── requirements-dev.txt
```

---

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | `mysql+pymysql://root:@localhost:3306/motomex` | URL de conexión a MySQL |
| `APP_NAME` | `Motomex API` | Nombre de la aplicación |
| `TEST_DATABASE_URL` | — | URL de la BD de tests (solo para pytest) |

---

## Despliegue en producción (Docker)

El backend está dockerizado para correr en cualquier servidor sin XAMPP. La imagen se construye a partir de los archivos `Dockerfile`, `docker-entrypoint.sh` y `.dockerignore` (el `docker-compose.yml` es **solo para pruebas locales** —levanta API + un MySQL de prueba juntos— y no se usa en el servidor).

### Configuración: variables de entorno, nunca `.env`

En producción la configuración **no** se lee de `.env` (ese archivo es solo local y está excluido de git y de la imagen por `.gitignore` y `.dockerignore`). Define estas variables como **variables de entorno en tu plataforma de despliegue**:

| Variable | Obligatoria | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Sí | `mysql+pymysql://USUARIO:CONTRASENA@HOST:3306/motomex` |
| `APP_NAME` | No | `Motomex API` |

> La nomenclatura completa de `DATABASE_URL` (qué es cada parte) está documentada como comentario al final de `.env`. Si la contraseña tiene caracteres especiales (`@ : / # ?`), URL-encodéalos.

### Migraciones automáticas

Al arrancar, el contenedor ejecuta `docker-entrypoint.sh`, que corre `alembic upgrade head` **antes** de levantar el servidor. No hay paso manual de migraciones en el servidor; basta con que la BD exista y sea accesible vía `DATABASE_URL`.

### Despliegue en Hostinger con Coolify (alto nivel)

[Coolify](https://coolify.io/) es un PaaS self-hosted (el mismo estilo del n8n que corre en el VPS). Pasos generales:

1. **Base de datos:** crea un recurso **MySQL 8** en Coolify (collation `utf8mb4_unicode_ci`). Anota usuario, contraseña, host (el nombre interno del servicio) y el nombre de la BD (`motomex`).
2. **Aplicación:** crea un recurso nuevo desde el **repositorio de GitHub**, apuntando al directorio `API-server/` y su `Dockerfile`. Coolify reconstruye la imagen en cada push.
3. **Variables de entorno:** en la app, define `DATABASE_URL` (apuntando al MySQL del paso 1, puerto interno `3306`) y, opcionalmente, `APP_NAME`.
4. **Puerto y dominio:** expón el puerto **8000**, asigna un dominio/subdominio y activa **HTTPS** (Coolify gestiona el certificado Let's Encrypt automáticamente).
5. **Healthcheck:** la imagen ya expone `GET /health`; Coolify lo usa para saber si el contenedor está sano.
6. **n8n:** con el HTTPS activo, configura en el bot de n8n la URL pública (`https://<tu-dominio>`) como base para consumir la API.

> En el servidor, MySQL es un recurso **aparte** gestionado por Coolify; por eso allí no se usa el `docker-compose.yml` de este repo.

---

## Sesiones siguientes

Con XAMPP corriendo, desde `API-server/`:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```
