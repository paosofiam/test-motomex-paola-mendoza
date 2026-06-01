---
name: motomex-n8n-workflows
description: Usar al trabajar en `n8n-workflows/` o al crear/modificar cualquier JSON de workflow de n8n para importar/exportar en n8n Cloud o self-hosted (chatbot de WhatsApp Motomex que vende refacciones). Garantiza estructura JSON canónica verificada contra la doc oficial de n8n, credenciales solo por referencia (sin secretos), portabilidad Cloud↔self-hosted, y un muro infranqueable: NUNCA tocar `API-server/`, NUNCA levantar servidores/BD locales — el backend es una caja negra en producción consultada solo vía su API.
---

# Workflows de n8n Motomex (JSON import/export · Cloud y self-hosted)

Esta skill gobierna la generación de **workflows de n8n en JSON** listos para importar/exportar en **n8n Cloud y self-hosted**. El JSON debe ser válido e importable *tal cual*, sin pasos manuales de arreglo. La doc oficial de n8n (`https://docs.n8n.io`) es la **única fuente de verdad** para nodos; este archivo es la única fuente de verdad para las reglas del proyecto.

Asumimos **siempre la última versión de n8n**: los workflows se importan en cualquier instancia, así que no nos atamos a una versión concreta.

## Antes de diseñar cualquier nodo

1. **Consulta la doc oficial del nodo** en `https://docs.n8n.io` (sección Integrations) **antes** de escribirlo. Confirma contra la doc: el `type` exacto (con namespace), el `typeVersion` (usa la **última estable** documentada) y los `parameters` reales.
2. **NUNCA inventes** campos, parámetros, `type` ni `typeVersion`. Si la doc no lo confirma, no va.
3. Si un nodo no existe como built-in y exige un community/custom node, **detente y avísalo** (rompe portabilidad — ver abajo). No lo asumas instalado.

## Muro sobre `API-server/` (no negociable)

Al trabajar en n8n, **`API-server/` y todo su contenido son INTOCABLES**: ni una extensión de archivo, ni una ubicación, ni un punto y coma. Trata ese código como si **no existiera**.

- **NUNCA** edites, muevas, renombres ni leas-para-modificar nada bajo `API-server/`.
- **NUNCA** levantes un servidor local (uvicorn, etc.) ni una base de datos local (MySQL/XAMPP) "para probar".
- El backend, para n8n, es una **caja negra ya desplegada en producción**.

## El backend es una API en producción

La única realidad del backend es la API desplegada:

- **Base:** `https://api-test-motomex.paosofiam.com/`
- **Docs (OpenAPI):** `https://api-test-motomex.paosofiam.com/docs`

Reglas:
- Los nodos **HTTP Request** del workflow apuntan **siempre** a esa base, NUNCA a `localhost`.
- Para dar de alta o consultar datos durante el desarrollo, usa **`curl`** contra esa API desde la terminal — NUNCA tocando MySQL ni el código:

```bash
# Consultar (GET)
curl -s "https://api-test-motomex.paosofiam.com/productos"

# Crear (POST con JSON)
curl -s -X POST "https://api-test-motomex.paosofiam.com/leads" \
  -H "Content-Type: application/json" \
  -d '{ "...": "..." }'
```

- Antes de cablear un endpoint en un nodo, **verifica su contrato real** en `/docs` (ruta, método, body, forma de respuesta). No asumas el shape.

## Estructura JSON canónica (no negociable)

Verificado contra la doc oficial de n8n. Todo workflow exportado debe respetar esta forma.

### Top-level

- **Requeridos para importar:** `name` (string), `nodes` (array), `connections` (object).
- **Incluir siempre:** `settings` con `{ "executionOrder": "v1" }`, y `pinData` con `{}`.
- **Opcionales según el caso:** `active` (boolean), `tags` (array), `meta`, `versionId`.
- **NO** hardcodear `id` de workflow (deja que la instancia lo genere al importar). **NO** fijar un `meta.instanceId` ajeno.

### Node object (cada entrada de `nodes`)

- **Requeridos:** `id` (uuid string, único en el workflow), `name` (string, único — es la clave usada en `connections`), `type` (namespaced), `typeVersion` (number, explícito), `position` (`[x, y]`), `parameters` (object).
- **Opcionales:** `credentials`, `disabled`, `notes`, `webhookId` (en triggers de webhook).
- **Namespacing del `type`:** built-in core → `n8n-nodes-base.*` (p. ej. `n8n-nodes-base.httpRequest`); nodos de IA/LangChain → `@n8n/n8n-nodes-langchain.*`. Community/custom solo con aviso explícito.

### `connections`

Keyed por **nombre del nodo ORIGEN** → tipo de conexión (`main`, o tipos de IA como `ai_tool`, `ai_languageModel`, `ai_memory`, `ai_outputParser`…) → **arreglo de arreglos** de `{ node, type, index }`.

```json
"connections": {
  "Webhook": {
    "main": [
      [
        { "node": "HTTP Request", "type": "main", "index": 0 }
      ]
    ]
  }
}
```

- El `node` destino se referencia por **nombre**, no por `id`.
- El arreglo externo = salidas del nodo; el interno = destinos de esa salida. La mayoría de nodos usan `index: 0`.

## Credenciales (NUNCA secretos)

En el JSON, las credenciales viajan **solo por referencia** — jamás el secreto:

```json
"credentials": {
  "tipoDeCredencial": { "id": "<placeholder-id>", "name": "<nombre legible>" }
}
```

- **NUNCA** incluyas API keys, tokens, passwords ni headers `Authorization` con valores reales en `parameters` ni en ningún lado del JSON.
- El `tipoDeCredencial` es el tipo real de n8n (p. ej. `httpHeaderAuth`, `slackApi`); confírmalo en la doc del nodo.
- Documenta en `notes` del nodo (o en un nodo Sticky Note) **qué credenciales debe crear** quien importe el workflow.

## Portabilidad Cloud ↔ self-hosted

- `typeVersion` **siempre explícito** en cada nodo (un import a una versión distinta no debe degradarse en silencio).
- **Evita** community/custom nodes salvo necesidad real y documentada — no estarán instalados en otra instancia.
- Los `id` de credencial son **por instancia**: al importar requieren remapeo manual. Usa placeholders y un `name` claro para que el remapeo sea obvio.
- `meta.instanceId` es una huella por instalación: no lo trates como significativo ni lo copies de otra instancia.

## Convención de carpeta `n8n-workflows/`

- **Un workflow por archivo** `.json`, nombre en `kebab-case` descriptivo (p. ej. `chatbot-ventas-whatsapp.json`).
- El archivo es JSON **estricto e importable tal cual**: sin comentarios, sin trailing commas, sin secretos.
- Nada de esta carpeta toca ni depende de `API-server/`.

## Checklist antes de entregar
- [ ] JSON válido (parsea) e importable tal cual en Cloud y self-hosted.
- [ ] `type`, `typeVersion` y `parameters` de **cada nodo** verificados contra la doc oficial de n8n.
- [ ] Ningún archivo de `API-server/` tocado; ningún servidor/BD local levantado.
- [ ] HTTP Request apuntan a `https://api-test-motomex.paosofiam.com/`; contratos confirmados en `/docs`.
- [ ] Sin secretos en el JSON; credenciales solo por referencia `{ id, name }`.
- [ ] `connections` referencian nodos por **nombre** y la estructura arreglo-de-arreglos es correcta.
- [ ] `settings.executionOrder = "v1"` y `pinData = {}` presentes; sin `id`/`instanceId` ajenos hardcodeados.
