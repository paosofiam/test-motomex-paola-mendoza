## Stack de Backend API

- Motor de Base de datos: MySQL (visible desde phpmyadmin y MySQL)
- Framework de backend: FastAPI
- Arquitectura: capas **router → service → model**, siguiendo la estructura estándar y las mejores prácticas de FastAPI. **No existe una capa de _controllers_** (FastAPI no es un framework MVC): lo que une los endpoints (routers) con los modelos son los **services**.
  - Modelos (capa de datos): **tablas ORM puras** de SQLAlchemy (columnas + relationships); definen el mapeo a la BD y exponen a lo sumo `get_by_id` (lookup por PK + `deleted_at IS NULL`). Las queries filtradas, la escritura con lógica (`create`/`update`/`delete`) y la orquestación multi-entidad NO viven aquí, sino en la capa Services, siguiendo la práctica estándar de FastAPI (las operaciones de datos son funciones que reciben `Session`, no métodos del modelo ORM).
  - Routers (frontera HTTP): declaran rutas con `APIRouter`, validan petición/respuesta con Pydantic, fijan status HTTP y header `Location`, y delegan la traducción de errores a RFC 7807 en los handlers de excepciones registrados.
  - Services (capa de orquestación / lógica de negocio): median entre routers y modelos; reciben los schemas ya validados, **construyen y ejecutan las queries filtradas (`search`, lookups con `ORDER BY`/`LIMIT`), las escrituras (`create`/`update`/`delete`) y la reconciliación de tablas de relación** (delegando helpers genéricos y la resolución de catálogos a `core/resolvers.py`), y construyen el body de respuesta (conversión a MXN, campos derivados). No conocen HTTP ni importan nada de FastAPI.
  - Vistas: Serán el chat de whatsapp controlado por el chatbot de n8n.

## Convenciones de nomenclaturas

| Elemento                | Convención                                                           | Ejemplo                                   |
| ----------------------- | -------------------------------------------------------------------- | ----------------------------------------- |
| Tablas DB               | `snake_case`, plural, español sin acentos                            | `productos`, `leads`, `pre_ordenes`       |
| Columnas DB             | `snake_case`; dominio en español, técnico en inglés                  | `marca`, `precio`, `created_at`           |
| Clases (general)        | `PascalCase`, singular                                               | `Producto`, `Lead`, `Chat`                |
| Funciones y métodos     | `snake_case` (PEP 8); verbo en inglés                                | `get_all()`, `get_by_id()`, `create()`    |
| Variables y propiedades | `snake_case` (PEP 8)                                                 | `user_id`, `total_amount`, `is_active`    |
| Carpeta de modelos      | `snake_case`, plural                                                 | `models/`                                 |
| Archivo de modelo       | `snake_case`, singular, sufijo `_model`                              | `product_model.py`, `lead_model.py`       |
| Clase de modelo         | `PascalCase`, singular, sufijo `Model`                               | `ProductModel`, `LeadModel`               |
| Carpeta de routers      | `snake_case`, plural                                                 | `routers/`                                |
| Archivo de router       | `snake_case`, plural (nombre del recurso)                            | `productos.py`, `leads.py`                |
| Instancia de router     | `router` (una por módulo de recurso; se accede `productos.router`)   | `router = APIRouter(prefix="/productos")` |
| Carpeta de servicios    | `snake_case`, plural                                                 | `services/`                               |
| Archivo de servicio     | `snake_case`, singular, sufijo `_service`                            | `producto_service.py`, `lead_service.py`  |
| Funciones de servicio   | `snake_case` (PEP 8), verbo en inglés, a nivel de módulo (sin clase) | `search()`, `get_by_id()`, `create()`     |

## Base de datos

> Para la especificación estructural completa (tablas, columnas, tipos, FKs, columnas estándar, valores por defecto, seeders y diagrama entidad-relación), véase [`er_diagram.md`](./er_diagram.md). Esta sección documenta únicamente los **por qués** de las decisiones de lógica de negocio que afectan al modelo de datos.

- **Precios y montos en centavos**: `productos.precio`, `monedas.tipo_de_cambio` y `pre_ordenes.total` se almacenan como `int` en centavos para evitar los errores de redondeo propios de los tipos flotantes (`0.1 + 0.2 ≠ 0.3`), garantizando aritmética exacta en cálculos, conversiones y persistencia. El cliente de la API formatea el decimal al presentarlo al usuario.
- **Pre-órdenes en MXN**: `pre_ordenes.total` se persiste en MXN ya convertido desde la moneda original vía `tipo_de_cambio`, porque el chatbot opera comercialmente en México. Almacenar el total ya convertido evita recalcular conversiones si los tipos de cambio del catálogo cambian, y deja un registro fiel del monto que el cliente aceptó en ese momento.
- **Formato de teléfono E.164**: `leads.telefono` respeta E.164 (máx. 15 caracteres, prefijo `+`) por ser el estándar de la ITU y el formato nativo de WhatsApp Business API. Cualquier otro formato exigiría normalización constante en la integración.
- **Identificadores de WhatsApp inmutables**: `leads.chat_whatsapp_id` y `chats.chat_whatsapp_id` no se modifican tras la creación porque son asignados por WhatsApp y representan la identidad del canal de conversación del lado del cliente; editarlos rompería la trazabilidad con los mensajes históricos. Ambos deben ser indexables para búsqueda directa desde el chatbot.
- **Un solo chat activo por `chat_whatsapp_id`**: aunque la relación `leads → chats` es 1:N a nivel relacional, la lógica impone un único chat activo simultáneo porque cada chat representa una sesión conversacional comercial coherente; chats paralelos fragmentarían el estado y harían ambiguo cuál continuar al recibir un mensaje nuevo. `POST /chats` es **idempotente**: si ya existe un chat activo con el mismo `lead_id` **o** `chat_whatsapp_id`, NO crea ni borra — devuelve el existente (`200 OK`). Reemplazarlo exige soft-deletear el anterior antes vía `DELETE` (`create` nunca lo elimina). La clave incluye `chat_whatsapp_id` además de `lead_id` porque un mismo identificador de WhatsApp puede llegar con `lead_id` distintos (p. ej. el fan-out del bot) y aun así debe deduplicar. Por eso las consultas por `chat_whatsapp_id` o `lead_id` retornan a lo sumo uno (`created_at DESC LIMIT 1`).
- **Un solo lead activo por `chat_whatsapp_id`**: simétrico al de chats. `POST /leads` es **idempotente**: si ya existe un lead activo con ese `chat_whatsapp_id`, devuelve el existente (`200 OK`) sin crear otro; para enriquecerlo se usa `PATCH /leads/{id}` sobre su `id`. Los leads **no se borran** vía API (no hay `DELETE /leads`), así que la unicidad se mantiene sin reemplazo. La consulta `GET /leads?chat_whatsapp_id=` retorna a lo sumo uno (`created_at DESC LIMIT 1`). Nota: la idempotencia se valida en la capa service (check-then-insert); MySQL no soporta índice UNIQUE parcial con `deleted_at IS NULL`, así que persiste una pequeña ventana TOCTOU bajo peticiones simultáneas del mismo `chat_whatsapp_id` (misma limitación en chats).
- **Identidad de vehículos `(modelo, marca, anio)`**: `vehiculos` lleva un UNIQUE compuesto sobre la tripleta porque la compatibilidad de refacciones es sensible al año (Versa Nissan 2010 ≠ Versa Nissan 2011); tratar al modelo sin año perdería precisión y produciría recomendaciones erróneas del chatbot. Esta unicidad también permite que el `find-or-create` sobre vehículos sea determinista.
- **Catálogos sin delete**: las tablas catálogo (`marcas`, `monedas`, `ciudades`, `estados`, `vehiculos`, `categorias`, `intenciones_de_compra_de_leads`, `chat_statuses`) no admiten delete (ni soft ni hard) porque sus registros son **constantes del sistema** referenciadas por entidades históricas; eliminarlos dejaría FKs colgantes o forzaría re-mapeos masivos. Nuevos valores solo se insertan vía find-or-create al crear entidades principales.
- **Soft delete en lugar de hard delete**: todas las eliminaciones usan `deleted_at` porque el dominio incluye datos comerciales históricos (leads, chats, pre-órdenes) cuya destrucción permanente impediría auditoría, análisis de conversión y recuperación ante errores operativos. Un elemento se considera activo cuando `deleted_at IS NULL`.
- **Tablas de relación con `id` y columnas estándar propias**: las tablas de relación heredan las mismas columnas estándar (`id`, `created_at`, `updated_at`, `deleted_at`) que las entidades para permitir auditar cuándo se creó/modificó cada vínculo y soft-eliminarlo sin perder la fila histórica (ej. un producto puede dejar de ser compatible con un vehículo sin borrar el registro de que alguna vez lo fue).
- **`pre_ordenes_productos.cantidad`**: la tabla incluye una columna `cantidad: int not_null` además de las dos FKs porque una pre-orden puede pedir N unidades del mismo producto; consolidar en una sola fila por `(pre_orden, producto)` es más limpio que insertar N filas duplicadas y permite calcular el total con una sola operación por producto.

## Modelos

La presente sección detalla los modelos del proyecto con sus métodos permitidos. **Todos los modelos
son tablas ORM puras** y exponen a lo sumo `get_by_id` (lookup por PK + `deleted_at IS NULL`). El
filtrado, las escrituras con lógica (`create`/`update`/`delete`) y la orquestación viven en
`*_service.py`; el find-or-create de catálogos y los helpers genéricos en `core/resolvers.py`. El
precedente de la migración es `producto`.

| Modelo                         | Métodos     |
| ------------------------------ | ----------- |
| `ProductoModel`                | `get_by_id` |
| `LeadModel`                    | `get_by_id` |
| `ChatModel`                    | `get_by_id` |
| `PreOrdenModel`                | — (sin métodos) |
| `VehiculoModel`                | `get_by_id` |
| `MarcaModel`                   | `get_by_id` |
| `MonedaModel`                  | `get_by_id` |
| `CiudadModel`                  | `get_by_id` |
| `IntencionDeCompraDeLeadModel` | `get_by_id` |
| `CategoriaModel`               | `get_by_id` |
| `ChatStatusModel`              | `get_by_id` |

> Los catálogos crecen solo por `resolvers.find_or_create_*` (Tier 2) o por seeder (Tier 1); su
> `get_by_id` lo usan los services para validar FKs Tier 1. `EstadoModel` no tiene ni `get_by_id`
> (se resuelve por `resolvers.find_estado`, nombre o abreviación).

**Notas** (los invariantes se mantienen, pero ahora los garantiza la capa service / `resolvers`):

- Todos los `create` guardan el mismo timestamp en `created_at` y `updated_at` (un único `ts = _now()`).
- Todos los `update` refrescan `updated_at`. Todos los `delete` son **soft delete** (`deleted_at`), **NUNCA** hard delete. Un elemento está activo cuando `deleted_at IS NULL`.
- El chat activo más reciente se resuelve en `chat_service` con `ORDER BY created_at DESC LIMIT 1` (regla de un solo chat activo por `chat_whatsapp_id`). `chat_service.create` es **idempotente** (por `lead_id` o `chat_whatsapp_id`) y **nunca** soft-deletea el anterior; reemplazar exige `chat_service.delete`.
- `lead_service.create` es **idempotente** por `chat_whatsapp_id` (devuelve el lead activo existente sin crear otro) y `lead_service.get_by_chat_whatsapp_id` devuelve **un solo** lead activo (`ORDER BY created_at DESC LIMIT 1`, 404 si no hay); respalda el endpoint `GET /leads`.

## Endpoints del proyecto

> Para la especificación técnica completa de endpoints (tipos abreviados, tabla de endpoints, formato de respuestas REST, formato de errores RFC 7807, política Tier 1/2/3 y política find-or-create/find-or-fail), véase [`endpoints.md`](./endpoints.md). Esta sección documenta únicamente los **por qués** de las decisiones de diseño de lógica de negocio detrás de esos endpoints.

- **Precios en MXN en todas las respuestas**: la API siempre retorna precios convertidos a MXN vía `tipo_de_cambio`, independientemente de la moneda original. Hacer la conversión en la capa de API libera al LLM consumidor de conocer las tasas vigentes, elimina una clase entera de errores y garantiza precios consistentes entre llamadas al mismo producto.
- **Política Tier 1/2/3 para catálogos**: clasifica los catálogos según tamaño/dinamismo para optimizar tokens y roundtrips del LLM consumidor. **Tier 1** (pequeños y estáticos como `monedas`, `chat_statuses`) viaja por ID porque el LLM los conoce vía system prompt. **Tier 2** (medianos/dinámicos como `marcas`, `categorias`, `estados`) viaja por string con normalización determinista en la API, evitando un `GET` previo solo para obtener un ID; `estados` admite además resolución por abreviación (ej. `"NL"`, `"CDMX"`) y solo viaja anidado en el objeto `{ciudad, estado}`. **Tier 3** (entidades dinámicas como `productos`, `leads`) viaja por `id` con campos legibles incluidos en respuestas para que el LLM pueda razonar sin mantener mapeos en memoria.
- **Find-or-create vs find-or-fail según el flujo**: la política depende de si el campo representa **inventario** (donde inventar registros sería un error de negocio) o **catálogo conversacional** (donde la captura natural debe crear lo que falte). `POST /productos` y los campos `vehiculo` y `ciudad` de leads usan find-or-create porque el chatbot necesita fluidez al capturar marcas, vehículos o ciudades nuevos. La `ciudad` viaja como `{ciudad, estado}`: se resuelve el estado (por nombre o abreviación) y se crea la ciudad bajo él; si el estado no se reconoce, se aplica **éxito parcial** (la ciudad se omite, el recurso se crea igual y se avisa por header `Warning`) en vez de un `422`, porque una ciudad no resuelta no debe bloquear el alta del producto/lead. `leads.productos_interes[]` usa **find-or-skip aditivo**: `productos` es inventario real y las menciones del cliente no deben contaminarlo (no es find-or-create), pero perder un lead por un producto inexistente es peor negocio que registrarlo incompleto, así que un modelo sin match se **omite** con aviso por header `Warning` (éxito parcial, como ciudades) y el lead se crea/actualiza igual (no es find-or-fail). En `PATCH` la vinculación es aditiva: combina los intereses nuevos con los ya capturados sin reemplazar ni borrar (un body vacío/omitido no cambia los previos; no hay remoción vía API), porque el interés del cliente solo se acumula a lo largo de la conversación. La misma semántica aditiva aplica a `leads.vehiculo[]`. `pre_ordenes.productos[].producto_id` exige el `id` exacto porque una pre-orden es un compromiso comercial cuantificable que no admite ambigüedad.
- **Vehículos siempre como objeto `{modelo, marca, anio}`**: el contrato externo transporta el objeto completo en peticiones y respuestas porque el LLM necesita el contexto para razonar (recomendar refacciones compatibles, validar año). Un `id` opaco forzaría un `GET /vehiculos/{id}` adicional cada vez. Esta forma también es la que habilita el `find-or-create` determinista por tripleta independientemente del estado de la BD.
- **REST puro sin wrapper de respuesta**: las respuestas devuelven el recurso directamente sin envolverlo en estructuras tipo `{"data": ..., "success": true}` porque el status HTTP ya es la fuente canónica de éxito/fracaso; un wrapper duplicaría la señal e introduciría una segunda fuente de verdad que podría divergir. Para un LLM consumidor, es además ruido tokenizado que no aporta semántica.
- **Errores en formato RFC 7807 (Problem Details)**: los errores `4xx`/`5xx` usan `application/problem+json` con la estructura estándar (`type`, `title`, `status`, `detail`, `instance` + campos extra como `field`, `value_received`) porque es el estándar IETF y su estructura tipada permite al LLM parsear el error, identificar el campo problemático y reintentar con un valor corregido sin tener que interpretar strings libres. El `value_received` es clave para flujos find-or-fail conversacionales (ej. corregir "Hiunday" → "Hyundai").
- **`leads.estado` derivado, no almacenado**: en las respuestas de `/leads` el campo `estado` se deriva transitivamente vía `leads.ciudad → ciudades.estado → estados.estado`, y no se acepta como campo independiente del body. La `ciudad` SÍ viaja en el body, pero como objeto `{ciudad, estado}`, donde el `estado` da contexto para resolver/crear la ciudad (no para almacenarse en `leads`). Derivar `estado` en la respuesta garantiza una única fuente de verdad y respeta la normalización 3NF; aceptarlo como campo suelto permitiría un par `(ciudad, estado)` inconsistente.
- **Éxito parcial vía header `Warning`, sin romper REST puro**: cuando un dato accesorio no se puede guardar (una ciudad cuyo estado no se reconoce, o un `producto_interes` que no existe en inventario), el recurso se crea/actualiza igual y el aviso viaja en el header HTTP `Warning` (RFC 7234, código 199) en lugar de un campo en el body. Así se preserva "el body ES el recurso" (sin wrapper) y el status HTTP sigue siendo la única señal de éxito, mientras el LLM consumidor recibe la notificación de lo que no se guardó. El valor del header se transcribe a ASCII porque los nombres de ciudad/estado mexicanos suelen llevar acentos no válidos en headers HTTP.

## Posibles Mejoras

1. **Método `update` en `ProductoModel`**: actualmente el modelo solo permite crear y borrar productos. Agregar `update` permitiría modificar precio, stock o especificaciones sin recrear el registro (y sin perder el `id` ni el historial de relaciones).
2. **Validación estricta de `telefono`**: además de la longitud E.164 ya documentada, definir regex de validación y normalización al ingresar (ej. eliminar espacios, garantizar prefijo `+`, rechazar caracteres no numéricos).
3. **Auth/Authz, paginación, rate limiting y formato estándar de respuestas de error**: capas transversales no contempladas en el contrato inicial. Especificar cuando el sistema deje el entorno controlado del chatbot interno.
4. **Paginación de métodos `get_all`**: actualmente el endpoint `GET` que retorna listas (`/productos`) no tiene paginación (`GET /leads` retorna un solo objeto por `chat_whatsapp_id`). Definir esquema (offset/limit, cursor, o page/per_page) y exponerlo vía query params + headers de respuesta (`X-Total-Count`, `Link` con `rel="next"`).
