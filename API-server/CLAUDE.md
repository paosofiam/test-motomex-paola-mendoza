# CLAUDE.md — API-server (reglas de implementación)

Reglas **vinculantes** para implementar el backend. Complementan el `CLAUDE.md` raíz (no lo repiten). La fuente de verdad sigue siendo `specs/` (`contracts.md`, `er_diagram.md`, `endpoints.md`); este archivo **resuelve las inconsistencias** que las specs dejaron abiertas en "Observaciones de revisión" y fija las decisiones canónicas para no re-derivarlas en cada cambio.

Para construir una capa, invoca la skill correspondiente:
- Modelos / migraciones / seeders → skill **`motomex-modelo-datos`**
- Controladores / routers / schemas → skill **`motomex-controlador-api`**
- Antes de hacer commit → skill **`motomex-revision-cumplimiento`**

## Decisiones canónicas (resuelven "Observaciones de revisión" de er_diagram.md)

1. **FKs con sufijo `_id` en TODAS las tablas.** Aunque la lista de entidades del diagrama las nombra sin sufijo (`marca`, `moneda`, `ciudad`, `intencion_de_compra`, `estado`), el storage real usa `<entidad>_id`: `marca_id`, `moneda_id`, `ciudad_id`, `intencion_de_compra_id`, `estado_id`, `chat_status_id`, `lead_id`, `producto_id`, `vehiculo_id`, `categoria_id`, `pre_orden_id`. El nombre **de dominio sin sufijo** (`marca`, `moneda`, `ciudad`, `estado`, `intencion_de_compra`) se usa solo en el **contrato externo** (JSON de respuesta), resuelto vía join.
2. **`productos.moneda_id`**: `FK int NOT NULL DEFAULT 1` (1 = MXN). No existe columna `moneda` string en la tabla. La respuesta devuelve `"moneda": "<abreviacion>"` resuelto por join.
3. **`pre_ordenes` NO lleva `moneda_id`.** `total` se persiste en **MXN ya convertido** (centavos). La conversión ocurre al calcular el total, no al leer.
4. **`leads` NO tiene columna `chat_id` ni `estado`/`estado_id`.** Ambos son campos **derivados de respuesta**:
   - `chat_id` = id del chat activo más reciente del lead (`chats` join `WHERE lead_id=? AND deleted_at IS NULL ORDER BY created_at DESC LIMIT 1`).
   - `estado` = join transitivo `leads.ciudad_id → ciudades.estado_id → estados.estado`.
5. **`leads.productos_interes[]`**: find-or-fail por `productos.modelo`. Si un modelo matchea varios productos, se persiste la relación en `leads_productos` con **todos** los matches → `leads_productos` puede tener más filas que strings recibidos.
6. **`chats` inmutables tras crear**: `PATCH /chats/{id}` solo toca `chat_status_id` y `resumen`. `lead_id` y `chat_whatsapp_id` nunca se actualizan (valídalo a nivel ORM/schema).
7. **Índices obligatorios** (créalos en la migración):
   - `leads.chat_whatsapp_id`, `chats.chat_whatsapp_id` (búsqueda directa).
   - `chats (lead_id, created_at DESC)` para `get_by_lead`/`get_by_chat_whatsapp_id` con LIMIT 1.
   - UNIQUE natural en catálogos Tier 2: `marcas.marca`, `categorias.categoria`, `ciudades.ciudad`, `estados.estado`, `monedas.abreviacion` (sobre el valor **ya normalizado**: lowercase/trim/sin acentos).
   - UNIQUE compuesto `vehiculos (modelo, marca_id, anio)`.
   - UNIQUE compuesto `(fk1, fk2)` en cada tabla de relación (evita duplicados).
8. **Mejora opcional (no rompe el contrato base):** filtros de compatibilidad en `GET /productos` o un `GET /productos/compatibles?vehiculo_modelo=&vehiculo_marca=&vehiculo_anio=`. Impleméntalo solo si se pide explícitamente; documenta que es extensión.

## Invariantes que cruzan toda la capa (violar uno rompe el contrato en otro lado)

- **Dinero = `int` centavos** en BD y en respuestas. Nunca `float`. `12999` = $129.99.
- **Respuestas siempre en MXN**: `mxn_centavos = round(precio * tipo_de_cambio / 100)` (entero). `tipo_de_cambio` también es centavos: MXN=100, USD=1700, EUR=2300.
- **Soft delete only**: delete ⇒ set `deleted_at`. Activo ⇔ `deleted_at IS NULL`. **Toda** query filtra `deleted_at IS NULL`.
- **Catálogos sin delete alguno**: `marcas`, `monedas`, `ciudades`, `estados`, `vehiculos`, `categorias`, `intenciones_de_compra_de_leads`, `chat_statuses`. Crecen solo por find-or-create.
- **Columnas estándar en TODAS las tablas** (incl. relación): `id` PK, `created_at`, `updated_at`, `deleted_at` (null). `create` ⇒ `created_at == updated_at`. `update` ⇒ refresca `updated_at`.
- **Un chat activo por lead**: crear chat nuevo exige soft-delete del previo. `get_by_lead`/`get_by_chat_whatsapp_id` ⇒ `ORDER BY created_at DESC LIMIT 1`.
- **Vehículos siempre como objeto** `{modelo, marca, anio}` en requests y responses; nunca id opaco. Identidad = UNIQUE `(modelo, marca_id, anio)`.
- **REST sin wrapper**: el body de éxito es el recurso. Errores = RFC 7807 `application/problem+json`. POST ⇒ header `Location`. PATCH ⇒ recurso completo.

## Matriz de métodos (NO agregar métodos fuera de esta lista)

| Modelo | Métodos permitidos |
| --- | --- |
| `ProductoModel` | `get_all`, `get_by_id`, `search`, `create`, `delete` |
| `LeadModel` | `get_by_id`, `search`, `create`, `update` |
| `ChatModel` | `get_by_id`, `get_by_chat_whatsapp_id`, `get_by_lead`, `create`, `update`, `delete` |
| `VehiculoModel` | `get_all`, `get_by_id`, `create` |
| `MarcaModel` | `get_all`, `get_by_id`, `create` |
| `MonedaModel` | `get_all`, `get_by_id`, `create` |
| `CiudadModel` | `get_all`, `get_by_id`, `create` |
| `IntencionDeCompraDeLeadModel` | `get_all`, `get_by_id`, `create` |
| `CategoriaModel` | `get_all`, `get_by_id`, `create` |
| `ChatStatusModel` | `get_all`, `get_by_id` |
| `PreOrdenModel` | `create` |

`ProductoModel` **no** tiene `update`. `ChatStatusModel` **no** tiene `create` (Tier 1 estático poblado por seeder). `PreOrdenModel` **solo** `create`. `LeadModel.search` respalda `GET /leads` (filtros por `chat_whatsapp_id`/`intencion_de_compra`).

## Clasificación Tier (catálogos)

- **Tier 1** (id en body → string en respuesta): `monedas`, `chat_statuses`, `intenciones_de_compra_de_leads`, `estados`.
- **Tier 2** (string ↔ string, API normaliza y resuelve a FK): `marcas`, `categorias`, `ciudades`, `vehiculos`.
- **Tier 3** (por `id`, respuesta incluye campos legibles): `productos`, `leads`, `chats`, `pre_ordenes`. Excepción: `leads.productos_interes[]` viaja como `[string]` (modelo) con find-or-fail.

## Convenciones de nombres (de contracts.md)

Dominio en **español** (la tabla de convenciones de `contracts.md` ya usa ejemplos en español y la matriz de modelos es la autoridad). Archivos `producto_model.py` → clases `ProductoModel`; routers `productos.py` (plural, instancia `router = APIRouter(...)`); services `producto_service.py` (funciones a nivel de módulo, sin clases). Métodos/vars `snake_case` con verbo en inglés (`get_by_id`, `create`).

## Entorno (de specs + scaffold real)

- Python 3.14 (`py -3.14`), venv en `API-server/.venv`, PowerShell en Windows.
- `app/database.py` ya expone `engine`, `SessionLocal`, `Base` (`DeclarativeBase`), `get_db()`. Reusa estos; no crees otros.
- `app/config.py` carga `.env` vía pydantic-settings: `settings.DATABASE_URL` y `settings.APP_NAME` (nombres en MAYÚSCULAS, como en el scaffold real). El `engine` ya usa `settings.DATABASE_URL`.
- **Arranca SIEMPRE desde `API-server/`** (`cd API-server` antes de `uvicorn app.main:app --reload` o de cualquier `python -c ...`). `env_file=".env"` es **relativo al cwd**: si corres desde la raíz del repo u otro dir, NO encuentra el `.env`, cae al default `root:@localhost` (sin contraseña) y falla con un engañoso `OperationalError (1045) Access denied ... (using password: NO)` que parece problema de credenciales de MySQL pero es solo el `.env` no cargado.
- MySQL de XAMPP, BD `motomex` (`utf8mb4_unicode_ci`) creada a mano en phpMyAdmin antes de migrar.
- `unidecode` (en requirements) es para la normalización Tier 2; `alembic` para migraciones.
- Puedes **leer** `.env` para obtener credenciales o diagnosticar problemas de conexión. No hay datos de producción sensibles ni API keys en este proyecto. **No commitees** `.env` (solo `.env.example`).
