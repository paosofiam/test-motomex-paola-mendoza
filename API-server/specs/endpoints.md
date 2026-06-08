# Endpoints del proyecto

Para entender las decisiones de lógica de negocio que dan forma a estos endpoints (por qué precios en MXN, por qué la política Tier 1/2/3, por qué find-or-create vs find-or-fail, etc.), véase [`contracts.md`](./contracts.md). Para la spec estructural de la base de datos referenciada por estos endpoints, véase [`er_diagram.md`](./er_diagram.md).

## Tipos abreviados

Los siguientes alias se usan en la tabla de endpoints:

- `Producto = {"id": int, "marca": string, "modelo": string, "precio": int, "moneda": string, "stock": int, "especificaciones": { "campo": "valor" }, "vehiculos": [{"modelo": string, "marca": string, "anio": int}], "categorias": [string], "ciudades": [{"ciudad": string, "estado": string}]}`
- `Lead = {"id": int, "chat_id": int, "chat_whatsapp_id": string, "nombre_whatsapp": string, "telefono": string, "nombre": string, "ciudad": string | null, "estado": string | null, "productos_interes": [string], "vehiculo": [{"modelo": string, "marca": string, "anio": int}], "direccion_envio": string, "intencion_de_compra": string}`
- `Chat = {"id": int, "lead_id": int, "chat_whatsapp_id": string, "status": string, "resumen": string}`
- `PreOrden = {"id": int, "lead_id": int, "total": int, "productos": [{"producto_id": int, "modelo": string, "cantidad": int}]}`

## Tabla de endpoints

| endpoint           | método | status éxito | query params opcionales              | body de petición                                                                                                                                                                                            | body de respuesta                                            |
| ------------------ | ------ | ------------ | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| /productos         | GET    | 200 OK       | `marca`, `precio_minimo`             | null                                                                                                                                                                                                        | `[Producto]`                                                 |
| /productos         | POST   | 201 Created  | —                                    | `{"marca": string, "modelo": string, "precio": int, "moneda_id": int, "stock": int, "especificaciones": { "campo": "valor" }, "vehiculos": [{"modelo": string, "marca": string, "anio": int}], "categorias": [string], "ciudades": [{"ciudad": string, "estado": string}]}` | `Producto`                                                   |
| /productos/{id}    | GET    | 200 OK       | —                                    | null                                                                                                                                                                                                        | `Producto`                                                   |
| /productos/{id}    | DELETE | 204 No Content | —                                  | null                                                                                                                                                                                                        | (sin body)                                                   |
| /leads             | GET    | 200 OK       | `chat_whatsapp_id`, `intencion_de_compra` | null                                                                                                                                                                                                  | `[Lead]`                                                     |
| /leads             | POST   | 201 Created  | —                                    | `{"chat_whatsapp_id": string, "nombre_whatsapp": string, "telefono": string, "nombre": string, "ciudad": {"ciudad": string, "estado": string}, "productos_interes": [string], "vehiculo": [{"modelo": string, "marca": string, "anio": int}], "direccion_envio": string, "intencion_de_compra_id": int}` | `Lead`                                              |
| /leads/{id}        | GET    | 200 OK       | —                                    | null                                                                                                                                                                                                        | `Lead`                                                       |
| /leads/{id}        | PATCH  | 200 OK       | —                                    | `{"nombre_whatsapp": string, "telefono": string, "nombre": string, "ciudad": {"ciudad": string, "estado": string}, "productos_interes": [string], "vehiculo": [{"modelo": string, "marca": string, "anio": int}], "direccion_envio": string, "intencion_de_compra_id": int}` | `Lead`                                              |
| /chats             | POST   | 201 Created  | —                                    | `{"lead_id": int, "chat_whatsapp_id": string, "chat_status_id": int, "resumen": string}`                                                                                                                    | `Chat`                                                       |
| /chats             | GET    | 200 OK       | `chat_whatsapp_id`                   | null                                                                                                                                                                                                        | `Chat`                                                       |
| /chats/{id}        | GET    | 200 OK       | —                                    | null                                                                                                                                                                                                        | `Chat`                                                       |
| /chats/{id}        | PATCH  | 200 OK       | —                                    | `{"chat_status_id": int, "resumen": string}`                                                                                                                                                                | `Chat`                                                       |
| /chats/{id}        | DELETE | 204 No Content | —                                  | null                                                                                                                                                                                                        | (sin body)                                                   |
| /pre_ordenes       | POST   | 201 Created  | —                                    | `{"lead_id": int, "total": int, "productos": [{"producto_id": int, "cantidad": int}]}`                                                                                                                      | `PreOrden`                                                   |

## Notas técnicas

### Conversión de moneda en respuestas

- Todos los productos deben ser retornados por la API con precio en pesos mexicanos (aplicando el `tipo_de_cambio` correspondiente si la moneda original es distinta), respetando la convención de centésimas.

### Formato de respuestas (REST puro)

- Las respuestas de éxito devuelven el recurso directamente como body, sin wrapper. El status HTTP es la fuente única de verdad sobre éxito o fracaso.
- Listas se devuelven como arrays JSON planos (`[Producto]`).
- Recursos individuales se devuelven como objeto JSON (`Producto`).
- `Content-Type: application/json`.
- **Respuestas POST**: además del body con el recurso creado, deben incluir el header HTTP `Location: /<recurso>/{id}` apuntando al recurso recién creado.
- **Respuestas PATCH**: retornan el recurso completo actualizado (estado posterior a la modificación).

### Formato de respuestas de error (RFC 7807 Problem Details)

Cualquier respuesta con status HTTP `4xx` o `5xx` retorna un body con la siguiente estructura, y header `Content-Type: application/problem+json`:

```json
{
  "type": "string (URI identificando el tipo de error)",
  "title": "string (resumen corto y legible)",
  "status": int (mismo código que el status HTTP),
  "detail": "string (descripción específica del caso)",
  "instance": "string (URI opcional del recurso afectado)"
}
```

Pueden agregarse campos extra propios del error (ej. `field`, `value_received`). Ejemplo de error de validación en `POST /leads` con marca inexistente:

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

### Endpoints de consulta de chats

- `GET /chats?chat_whatsapp_id=...` y `GET /chats/{id}` retornan siempre un único chat.
- En la consulta por `chat_whatsapp_id`, se devuelve el chat más reciente (orden `created_at DESC`, límite 1), conforme a la regla de un solo chat activo por lead.

### Campo `ciudad`/`estado` en `/leads` y `/productos`

- La **ciudad viaja como objeto `{ciudad, estado}`** en los bodies (campo `ciudad` en `/leads`, array `ciudades` en `/productos`). El `estado` dentro del objeto da el contexto para resolver/crear la ciudad (la BD exige `ciudades.estado_id NOT NULL`), y se resuelve por nombre o por abreviación (ej. `"Jalisco"` o `"JAL"`).
- El `estado` **no se acepta como campo independiente** a nivel raíz del body: en las respuestas de `/leads` se deriva automáticamente vía `leads.ciudad → ciudades.estado → estados.estado` (un `estado` suelto en el body se ignora). Aceptarlo por separado permitiría un par `(ciudad, estado)` inconsistente.

### Política de catálogos en peticiones y respuestas (Tier 1/2/3)

El consumidor de la API es un agente LLM. Para minimizar tokens y roundtrips, los catálogos se clasifican en tres niveles con tratamiento distinto:

- **Tier 1 — catálogos pequeños y estáticos** (`monedas`, `chat_statuses`, `intenciones_de_compra_de_leads`): el LLM conoce sus valores y IDs vía system prompt. Los **bodies de petición usan el ID** (ej. `moneda_id`, `chat_status_id`, `intencion_de_compra_id`). Las **respuestas devuelven solo el string** (ej. `"moneda": "MXN"`).
- **Tier 2 — catálogos medianos/dinámicos** (`marcas`, `categorias`, `ciudades`, `vehiculos`, `estados`): el LLM no los conoce de antemano (o son demasiados para fijar IDs). Los **bodies envían y las respuestas devuelven strings**. La API resuelve el string al FK internamente, aplicando normalización determinista (lowercase, trim, sin acentos) antes del lookup. `estados` admite además resolución por **abreviación** (ej. `"NL"`, `"CDMX"`) y solo aparece anidado dentro del objeto `{ciudad, estado}` (no tiene endpoint ni body propio).
- **Tier 3 — entidades dinámicas** (`productos`, `leads`, `chats`, `pre_ordenes`): se identifican siempre por `id` (int) en ambos sentidos. Las respuestas incluyen también los campos legibles (nombres) para que el LLM pueda razonar sobre ellas. Excepción documentada: `leads.productos_interes[]` se mantiene como `[string]` (modelo) con política **find-or-skip aditivo** (éxito parcial), porque expresa interés del cliente y la captura conversacional con nombre es más natural; un modelo que no exista en inventario no bloquea el lead, se omite con aviso.

### Política de resolución de strings (Tier 2 y excepciones Tier 3)

- `POST /productos` → **find-or-create** para `marca` (string), `vehiculos` (array de objetos `{modelo, marca, anio}`), `categorias` (array de strings) y `ciudades` (array de objetos `{ciudad, estado}`). En el caso de `vehiculos`, find-or-create resuelve la tripleta `(modelo, marca, anio)`; si la marca dentro de ese vehículo tampoco existe, se crea en cascada. Para cada ciudad, se resuelve el `estado` (por nombre o abreviación) y luego se hace find-or-create de la ciudad bajo ese estado. **Éxito parcial**: si el estado de una ciudad no se reconoce, esa ciudad se **omite** (el producto se crea igual) y se reporta vía header `Warning` (ver abajo) — no es un `422`.
- `POST/PATCH /leads` → el campo `vehiculo` (array de objetos `{modelo, marca, anio}`) y el campo `ciudad` (objeto `{ciudad, estado}`) son **find-or-create** (con cascade sobre `marca` en vehículos; con resolución de estado + éxito parcial en ciudad). Esto permite registrar vehículos y ciudades nuevos durante la captura conversacional del lead. El campo `productos_interes[]` es **find-or-skip aditivo** (ver caso específico abajo). En `PATCH`, las relaciones `productos_interes` y `vehiculo` se vinculan de forma **aditiva**: combinan lo enviado con lo ya existente, **nunca** reemplazan ni borran, y un body vacío/omitido las deja intactas (no hay remoción de relaciones vía API).
- **Todos los demás POST/PATCH** → **find-or-fail estricto**. Si el string no resuelve a un registro existente, la petición falla con `422 Unprocessable Entity` indicando el campo y el valor recibido. No se devuelven sugerencias; el agente reintenta con otro valor.
- Caso específico `leads.productos_interes[]`: **find-or-skip aditivo** por modelo. La tabla `productos` es inventario; un interés del cliente no autoriza crear producto (no es find-or-create), pero tampoco debe bloquear el registro del lead (no es find-or-fail): un modelo que no exista se **omite** y se reporta vía header `Warning` (éxito parcial, igual que ciudades), y el lead se crea/actualiza igual con su status normal (`201`/`200`). Si la búsqueda por `modelo` retorna más de un producto (ambigüedad de catálogo), se persiste la relación con todos los matches encontrados (criterio determinista).
- Caso específico `pre_ordenes.productos[].producto_id`: el agente debe consultar previamente `GET /productos` (con filtros si es necesario) para obtener el `id` exacto del producto. No hay resolución por string en pre-órdenes.
- Los `GET` no aplican esta política: siempre retornan strings ya resueltos.

### Éxito parcial y header `Warning`

- `POST /productos` y `POST/PATCH /leads` resuelven las ciudades con **éxito parcial**: si el `estado` de una ciudad no se reconoce (ni por nombre ni por abreviación), esa ciudad se **omite** del recurso (no se vincula) y el recurso se crea/actualiza igual con su status normal (`201`/`200`) — **no** es un error `422`. `POST/PATCH /leads` aplica el mismo éxito parcial a `productos_interes[]`: cada modelo que no exista en inventario se **omite** y el lead se crea/actualiza igual.
- El body de respuesta sigue siendo el recurso limpio (REST sin wrapper): no se le agrega ningún campo de aviso. La notificación viaja en el header HTTP **`Warning`** (RFC 7234, código `199`), con un texto por cada dato omitido, p. ej.: `199 - "No se guardo la ciudad 'Tijuana': estado 'Atlantis' no reconocido"` o `199 - "No se vinculó el producto de interés 'NoExiste': no existe en el inventario"`.
- El valor del header se transcribe a ASCII (los nombres de ciudad/estado mexicanos suelen llevar acentos, que no son válidos en un header HTTP).
- El consumidor LLM puede confirmar lo realmente guardado en el body: en `/productos`, el array `ciudades` de la respuesta refleja solo las vinculadas; en `/leads`, `ciudad`/`estado` salen `null` si la ciudad se omitió.

### Vehículos en bodies y respuestas

- Cualquier campo que represente un vehículo (en peticiones o respuestas, sea de `/leads`, `/productos` u otro endpoint futuro) debe transportarlo siempre como objeto `{"modelo": string, "marca": string, "anio": int}`. Esto da contexto completo al LLM y permite la resolución find-or-create determinista, independientemente de cómo esté normalizado en la base de datos.
