## Stack de Backend API

- Motor de Base de datos: MySQL (visible desde phpmyadmin y MySQL)
- Framework de backend: FastAPI
- Arquitectura: capas **router → service → model**, elegida por su _similitud_ con el patrón MVC pero siguiendo la estructura estándar y las mejores prácticas de FastAPI (FastAPI no es un framework MVC).
  - Modelos (capa de datos): ORM de SQLAlchemy + schemas/validaciones de Pydantic; encapsulan el acceso a la BD.
  - Routers (frontera HTTP; equivalen al "Controlador" de MVC): declaran rutas con `APIRouter`, validan petición/respuesta con Pydantic, fijan status HTTP y header `Location`, y delegan la traducción de errores a RFC 7807 en los handlers de excepciones registrados.
  - Services (capa de orquestación / lógica de negocio): median entre routers y modelos; reciben los schemas ya validados, llaman a modelos/`resolvers` y construyen el body de respuesta (conversión a MXN, campos derivados). No conocen HTTP ni importan nada de FastAPI.
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
- **Un solo chat activo por lead**: aunque la relación `leads → chats` es 1:N a nivel relacional, la lógica impone un único chat activo simultáneo porque cada chat representa una sesión conversacional comercial coherente; chats paralelos fragmentarían el estado y harían ambiguo cuál continuar al recibir un mensaje nuevo. Para crear uno nuevo, el anterior debe ser soft-deleted primero; por eso las consultas por `chat_whatsapp_id` o `lead_id` retornan a lo sumo uno (`created_at DESC LIMIT 1`).
- **Identidad de vehículos `(modelo, marca, anio)`**: `vehiculos` lleva un UNIQUE compuesto sobre la tripleta porque la compatibilidad de refacciones es sensible al año (Versa Nissan 2010 ≠ Versa Nissan 2011); tratar al modelo sin año perdería precisión y produciría recomendaciones erróneas del chatbot. Esta unicidad también permite que el `find-or-create` sobre vehículos sea determinista.
- **Catálogos sin delete**: las tablas catálogo (`marcas`, `monedas`, `ciudades`, `estados`, `vehiculos`, `categorias`, `intenciones_de_compra_de_leads`, `chat_statuses`) no admiten delete (ni soft ni hard) porque sus registros son **constantes del sistema** referenciadas por entidades históricas; eliminarlos dejaría FKs colgantes o forzaría re-mapeos masivos. Nuevos valores solo se insertan vía find-or-create al crear entidades principales.
- **Soft delete en lugar de hard delete**: todas las eliminaciones usan `deleted_at` porque el dominio incluye datos comerciales históricos (leads, chats, pre-órdenes) cuya destrucción permanente impediría auditoría, análisis de conversión y recuperación ante errores operativos. Un elemento se considera activo cuando `deleted_at IS NULL`.
- **Tablas de relación con `id` y columnas estándar propias**: las tablas de relación heredan las mismas columnas estándar (`id`, `created_at`, `updated_at`, `deleted_at`) que las entidades para permitir auditar cuándo se creó/modificó cada vínculo y soft-eliminarlo sin perder la fila histórica (ej. un producto puede dejar de ser compatible con un vehículo sin borrar el registro de que alguna vez lo fue).
- **`pre_ordenes_productos.cantidad`**: la tabla incluye una columna `cantidad: int not_null` además de las dos FKs porque una pre-orden puede pedir N unidades del mismo producto; consolidar en una sola fila por `(pre_orden, producto)` es más limpio que insertar N filas duplicadas y permite calcular el total con una sola operación por producto.

## Modelos

La presente sección detalla los modelos del proyecto con sus métodos permitidos.

| Modelo                         | Métodos                                                                             |
| ------------------------------ | ----------------------------------------------------------------------------------- |
| `ProductoModel`                | `get_all`, `get_by_id`, `search`, `create`, `delete`                                |
| `LeadModel`                    | `get_by_id`, `search`, `create`, `update`                                           |
| `ChatModel`                    | `get_by_id`, `get_by_chat_whatsapp_id`, `get_by_lead`, `create`, `update`, `delete` |
| `VehiculoModel`                | `get_all`, `get_by_id`, `create`                                                    |
| `MarcaModel`                   | `get_all`, `get_by_id`, `create`                                                    |
| `MonedaModel`                  | `get_all`, `get_by_id`, `create`                                                    |
| `CiudadModel`                  | `get_all`, `get_by_id`, `create`                                                    |
| `IntencionDeCompraDeLeadModel` | `get_all`, `get_by_id`, `create`                                                    |
| `CategoriaModel`               | `get_all`, `get_by_id`, `create`                                                    |
| `ChatStatusModel`              | `get_all`, `get_by_id`                                                              |
| `PreOrdenModel`                | `create`                                                                            |

**Notas**:

- Todos los métodos add/create deben guardar el mismo timestamp correspondiente en las columnas "created_at" y "updated_at" del elemento.
- Todos los métodos edit/update deben asegurar guardar el timestamp correspondiente en la columna "updated_at" del elemento a editar.
- Todos los métodos delete deben hacer soft delete en la base de datos guardando el timestamp correspondiente en la columna "deleted_at" del elemento o fila a eliminar de la tabla, **NUNCA** hard delete que destruya por completo el elemento. Un elemento se considera activo cuando `deleted_at IS NULL`.
- Los métodos `get_by_chat_whatsapp_id` y `get_by_lead` de `ChatModel` deben ordenar por `created_at DESC` y limitar la respuesta a **un único registro** (el chat más reciente), en cumplimiento de la regla de negocio de un solo chat activo por lead.
- El método `search` de `LeadModel` lista leads activos con filtros opcionales por `chat_whatsapp_id` e `intencion_de_compra` (string); respalda el endpoint `GET /leads`.

## Endpoints del proyecto

> Para la especificación técnica completa de endpoints (tipos abreviados, tabla de endpoints, formato de respuestas REST, formato de errores RFC 7807, política Tier 1/2/3 y política find-or-create/find-or-fail), véase [`endpoints.md`](./endpoints.md). Esta sección documenta únicamente los **por qués** de las decisiones de diseño de lógica de negocio detrás de esos endpoints.

- **Precios en MXN en todas las respuestas**: la API siempre retorna precios convertidos a MXN vía `tipo_de_cambio`, independientemente de la moneda original. Hacer la conversión en la capa de API libera al LLM consumidor de conocer las tasas vigentes, elimina una clase entera de errores y garantiza precios consistentes entre llamadas al mismo producto.
- **Política Tier 1/2/3 para catálogos**: clasifica los catálogos según tamaño/dinamismo para optimizar tokens y roundtrips del LLM consumidor. **Tier 1** (pequeños y estáticos como `monedas`, `chat_statuses`) viaja por ID porque el LLM los conoce vía system prompt. **Tier 2** (medianos/dinámicos como `marcas`, `categorias`) viaja por string con normalización determinista en la API, evitando un `GET` previo solo para obtener un ID. **Tier 3** (entidades dinámicas como `productos`, `leads`) viaja por `id` con campos legibles incluidos en respuestas para que el LLM pueda razonar sin mantener mapeos en memoria.
- **Find-or-create vs find-or-fail según el flujo**: la política depende de si el campo representa **inventario** (donde inventar registros sería un error de negocio) o **catálogo conversacional** (donde la captura natural debe crear lo que falte). `POST /productos` y `vehiculo` de leads usan find-or-create porque el chatbot necesita fluidez al capturar marcas o vehículos nuevos. `leads.productos_interes[]` usa find-or-fail porque `productos` es inventario real y menciones del cliente no deben contaminarlo. `pre_ordenes.productos[].producto_id` exige el `id` exacto porque una pre-orden es un compromiso comercial cuantificable que no admite ambigüedad.
- **Vehículos siempre como objeto `{modelo, marca, anio}`**: el contrato externo transporta el objeto completo en peticiones y respuestas porque el LLM necesita el contexto para razonar (recomendar refacciones compatibles, validar año). Un `id` opaco forzaría un `GET /vehiculos/{id}` adicional cada vez. Esta forma también es la que habilita el `find-or-create` determinista por tripleta independientemente del estado de la BD.
- **REST puro sin wrapper de respuesta**: las respuestas devuelven el recurso directamente sin envolverlo en estructuras tipo `{"data": ..., "success": true}` porque el status HTTP ya es la fuente canónica de éxito/fracaso; un wrapper duplicaría la señal e introduciría una segunda fuente de verdad que podría divergir. Para un LLM consumidor, es además ruido tokenizado que no aporta semántica.
- **Errores en formato RFC 7807 (Problem Details)**: los errores `4xx`/`5xx` usan `application/problem+json` con la estructura estándar (`type`, `title`, `status`, `detail`, `instance` + campos extra como `field`, `value_received`) porque es el estándar IETF y su estructura tipada permite al LLM parsear el error, identificar el campo problemático y reintentar con un valor corregido sin tener que interpretar strings libres. El `value_received` es clave para flujos find-or-fail conversacionales (ej. corregir "Hiunday" → "Hyundai").
- **`leads.estado` derivado, no almacenado**: el campo `estado` aparece en respuestas de `/leads` pero no se acepta en bodies porque se deriva transitivamente vía `leads.ciudad → ciudades.estado → estados.estado`. Aceptarlo permitiría un par `(ciudad, estado)` inconsistente; derivarlo siempre garantiza una única fuente de verdad y respeta la normalización 3NF.

## Posibles Mejoras

1. **Método `update` en `ProductoModel`**: actualmente el modelo solo permite crear y borrar productos. Agregar `update` permitiría modificar precio, stock o especificaciones sin recrear el registro (y sin perder el `id` ni el historial de relaciones).
2. **Validación estricta de `telefono`**: además de la longitud E.164 ya documentada, definir regex de validación y normalización al ingresar (ej. eliminar espacios, garantizar prefijo `+`, rechazar caracteres no numéricos).
3. **Auth/Authz, paginación, rate limiting y formato estándar de respuestas de error**: capas transversales no contempladas en el contrato inicial. Especificar cuando el sistema deje el entorno controlado del chatbot interno.
4. **Paginación de métodos `get_all`**: actualmente los endpoints `GET` que retornan listas (`/productos`, `/leads`) no tienen paginación. Definir esquema (offset/limit, cursor, o page/per_page) y exponerlo vía query params + headers de respuesta (`X-Total-Count`, `Link` con `rel="next"`).
