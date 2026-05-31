# Endpoints del proyecto

Para entender las decisiones de lógica de negocio que dan forma a estos endpoints (por qué precios en MXN, por qué la política Tier 1/2/3, por qué find-or-create vs find-or-fail, etc.), véase [`contracts.md`](./contracts.md). Para la spec estructural de la base de datos referenciada por estos endpoints, véase [`er_diagram.md`](./er_diagram.md).

## Tipos abreviados

Los siguientes alias se usan en la tabla de endpoints:

- `Producto = {"id": int, "marca": string, "modelo": string, "precio": int, "moneda": string, "stock": int, "especificaciones": { "campo": "valor" }}`
- `Lead = {"id": int, "chat_id": int, "chat_whatsapp_id": string, "nombre_whatsapp": string, "telefono": string, "nombre": string, "ciudad": string, "estado": string, "productos_interes": [string], "vehiculo": [{"modelo": string, "marca": string, "anio": int}], "direccion_envio": string, "intencion_de_compra": string}`
- `Chat = {"id": int, "lead_id": int, "chat_whatsapp_id": string, "status": string, "resumen": string}`
- `PreOrden = {"id": int, "lead_id": int, "total": int, "productos": [{"producto_id": int, "modelo": string, "cantidad": int}]}`

## Tabla de endpoints

| endpoint           | método | status éxito | query params opcionales              | body de petición                                                                                                                                                                                            | body de respuesta                                            |
| ------------------ | ------ | ------------ | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| /productos         | GET    | 200 OK       | `marca`, `precio_minimo`             | null                                                                                                                                                                                                        | `[Producto]`                                                 |
| /productos         | POST   | 201 Created  | —                                    | `{"marca": string, "modelo": string, "precio": int, "moneda_id": int, "stock": int, "especificaciones": { "campo": "valor" }, "vehiculos": [{"modelo": string, "marca": string, "anio": int}], "categorias": [string], "ciudades": [string]}` | `Producto`                                                   |
| /productos/{id}    | GET    | 200 OK       | —                                    | null                                                                                                                                                                                                        | `Producto`                                                   |
| /productos/{id}    | DELETE | 204 No Content | —                                  | null                                                                                                                                                                                                        | (sin body)                                                   |
| /leads             | GET    | 200 OK       | `chat_whatsapp_id`, `intencion_de_compra` | null                                                                                                                                                                                                  | `[Lead]`                                                     |
| /leads             | POST   | 201 Created  | —                                    | `{"chat_whatsapp_id": string, "nombre_whatsapp": string, "telefono": string, "nombre": string, "ciudad": string, "productos_interes": [string], "vehiculo": [{"modelo": string, "marca": string, "anio": int}], "direccion_envio": string, "intencion_de_compra_id": int}` | `Lead`                                              |
| /leads/{id}        | GET    | 200 OK       | —                                    | null                                                                                                                                                                                                        | `Lead`                                                       |
| /leads/{id}        | PATCH  | 200 OK       | —                                    | `{"nombre_whatsapp": string, "telefono": string, "nombre": string, "ciudad": string, "productos_interes": [string], "vehiculo": [{"modelo": string, "marca": string, "anio": int}], "direccion_envio": string, "intencion_de_compra_id": int}` | `Lead`                                              |
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

### Campo `estado` en `/leads`

- El campo `estado` no se acepta en el body de `/leads` (POST/PATCH) porque se deriva automáticamente de `ciudad` vía la relación `ciudades → estados`. Sí se incluye en las respuestas como valor calculado.

### Política de catálogos en peticiones y respuestas (Tier 1/2/3)

El consumidor de la API es un agente LLM. Para minimizar tokens y roundtrips, los catálogos se clasifican en tres niveles con tratamiento distinto:

- **Tier 1 — catálogos pequeños y estáticos** (`monedas`, `chat_statuses`, `intenciones_de_compra_de_leads`, `estados`): el LLM conoce sus valores y IDs vía system prompt. Los **bodies de petición usan el ID** (ej. `moneda_id`, `chat_status_id`, `intencion_de_compra_id`). Las **respuestas devuelven solo el string** (ej. `"moneda": "MXN"`).
- **Tier 2 — catálogos medianos/dinámicos** (`marcas`, `categorias`, `ciudades`, `vehiculos`): el LLM no los conoce de antemano. Los **bodies envían y las respuestas devuelven strings**. La API resuelve el string al FK internamente, aplicando normalización determinista (lowercase, trim, sin acentos) antes del lookup.
- **Tier 3 — entidades dinámicas** (`productos`, `leads`, `chats`, `pre_ordenes`): se identifican siempre por `id` (int) en ambos sentidos. Las respuestas incluyen también los campos legibles (nombres) para que el LLM pueda razonar sobre ellas. Excepción documentada: `leads.productos_interes[]` se mantiene como `[string]` (modelo) con política find-or-fail, porque expresa interés del cliente y la captura conversacional con nombre es más natural.

### Política de resolución de strings (Tier 2 y excepciones Tier 3)

- `POST /productos` → **find-or-create** en todos los FKs del producto: `marca` (string), `vehiculos` (array de objetos `{modelo, marca, anio}`), `categorias` (array de strings), `ciudades` (array de strings). En el caso de `vehiculos`, find-or-create resuelve la tripleta `(modelo, marca, anio)`; si la marca dentro de ese vehículo tampoco existe, se crea en cascada.
- `POST/PATCH /leads` → el campo `vehiculo` (array de objetos `{modelo, marca, anio}`) es **find-or-create** con la misma cascade sobre `marca`. Esto permite registrar vehículos nuevos durante la captura conversacional del lead. El resto de campos string en `/leads` siguen find-or-fail.
- **Todos los demás POST/PATCH** → **find-or-fail estricto**. Si el string no resuelve a un registro existente, la petición falla con `422 Unprocessable Entity` indicando el campo y el valor recibido. No se devuelven sugerencias; el agente reintenta con otro valor.
- Caso específico `leads.productos_interes[]`: find-or-fail por modelo. La tabla `productos` es inventario; un interés del cliente no autoriza crear producto. Si la búsqueda por `modelo` retorna más de un producto (ambigüedad de catálogo), se persiste la relación con todos los matches encontrados (criterio determinista).
- Caso específico `pre_ordenes.productos[].producto_id`: el agente debe consultar previamente `GET /productos` (con filtros si es necesario) para obtener el `id` exacto del producto. No hay resolución por string en pre-órdenes.
- Los `GET` no aplican esta política: siempre retornan strings ya resueltos.

### Vehículos en bodies y respuestas

- Cualquier campo que represente un vehículo (en peticiones o respuestas, sea de `/leads`, `/productos` u otro endpoint futuro) debe transportarlo siempre como objeto `{"modelo": string, "marca": string, "anio": int}`. Esto da contexto completo al LLM y permite la resolución find-or-create determinista, independientemente de cómo esté normalizado en la base de datos.
