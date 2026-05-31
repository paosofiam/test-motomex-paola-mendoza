---
name: motomex-controlador-api
description: Usar al crear o modificar la CAPA DE API del backend Motomex (API-server) — controladores/routers FastAPI, schemas Pydantic de request/response, manejo de errores, o cualquier endpoint de /productos, /leads, /chats, /pre_ordenes. Garantiza REST sin wrapper, errores RFC 7807, header Location, conversión de precios a MXN, política Tier 1/2/3 y find-or-create/find-or-fail definidos en API-server/specs.
---

# Capa de API Motomex (controladores · routers · schemas)

Asegura que cada endpoint cumpla `API-server/specs/endpoints.md` (tabla de endpoints, formatos, política Tier/resolución) y los por qués de `contracts.md`. Decisiones canónicas en `API-server/CLAUDE.md`.

## Antes de escribir código

1. Localiza el endpoint en la **tabla de `endpoints.md`**: método, status de éxito, query params, body de petición, body de respuesta (alias `Producto`/`Lead`/`Chat`/`PreOrden`).
2. Identifica el Tier de cada campo del body (define si viaja por id o por string).
3. Decide find-or-create vs find-or-fail por campo (ver abajo).
4. Nombres: archivo `*_controller.py`, clase `*Controller`, instancia `*_router` (español: `ProductoController`, `producto_router`).

## Contrato REST (no negociable)

- **Sin wrapper**: el body de éxito ES el recurso (`Producto`) o un array plano (`[Producto]`). Nunca `{"data": ..., "success": true}`.
- **Status como única señal de éxito**: usa los de la tabla (`200`, `201`, `204`).
- **POST** ⇒ status `201` + header `Location: /<recurso>/{id}`.
- **PATCH** ⇒ `200` + recurso completo ya actualizado.
- **DELETE** ⇒ `204` sin body (y es **soft delete**).
- `Content-Type: application/json` en éxito.

## Errores RFC 7807 (Problem Details)

Todo `4xx`/`5xx` ⇒ `Content-Type: application/problem+json` con:

```json
{ "type": "URI", "title": "...", "status": 422, "detail": "...", "instance": "/leads",
  "field": "vehiculo[0].marca", "value_received": "Hiunday" }
```

- `value_received` es clave en flujos find-or-fail (deja que el LLM corrija "Hiunday"→"Hyundai" y reintente).
- Implementa esto con **exception handlers / decoradores** (contracts.md pide manejo de excepciones con decoradores). Centraliza en `app/core/` un `ProblemException` + un `@app.exception_handler` que serialice a problem+json. No devuelvas el `HTTPException` por defecto de FastAPI (no es problem+json).
- Recursos no encontrados ⇒ `404`; string Tier 2/Tier 3 que no resuelve en flujo find-or-fail ⇒ `422` con `field` + `value_received`.

## Conversión de precios → MXN (SIEMPRE en respuestas)

Toda respuesta con precio lo devuelve en **MXN centavos**, sin importar la moneda original:

```python
def a_mxn_centavos(precio: int, tipo_de_cambio: int) -> int:
    # tipo_de_cambio en centavos: MXN=100, USD=1700, EUR=2300
    return round(precio * tipo_de_cambio / 100)
```

`precio` se mantiene `int` en toda la respuesta (centavos). El cliente formatea el decimal. `pre_ordenes.total` ya viene convertido a MXN desde su `create`.

## Política Tier 1/2/3

| Tier | Catálogos | En request | En response |
| --- | --- | --- | --- |
| 1 | `monedas`, `chat_statuses`, `intenciones_de_compra_de_leads`, `estados` | `*_id` (int) | string |
| 2 | `marcas`, `categorias`, `ciudades`, `vehiculos` | string | string |
| 3 | `productos`, `leads`, `chats`, `pre_ordenes` | `id` (int) | `id` + campos legibles |

Excepción: `leads.productos_interes[]` viaja como `[string]` (modelo) en ambos sentidos.

### Normalización determinista Tier 2
Antes de cualquier lookup/creación de string Tier 2, normaliza: **lowercase + trim + sin acentos** (`unidecode`). El UNIQUE de la BD está sobre el valor normalizado, así que normaliza igual en find y en create.

```python
from unidecode import unidecode
def normalizar(s: str) -> str:
    return unidecode(s).strip().lower()
```

## Find-or-create vs find-or-fail (por campo)

- **find-or-create** (catálogo conversacional, captura fluida):
  - `POST /productos`: `marca` (string), `vehiculos[]` (`{modelo,marca,anio}` — cascada: si la `marca` del vehículo no existe, créala), `categorias[]`, `ciudades[]`.
  - `POST/PATCH /leads`: campo `vehiculo[]` (misma cascada sobre `marca`).
- **find-or-fail** (todo lo demás). Si no resuelve ⇒ `422` con `field`+`value_received`.
  - `leads.productos_interes[]`: find-or-fail por `productos.modelo`. Si matchea **varios** productos, persiste la relación con **todos** (no falles por ambigüedad).
  - `pre_ordenes.productos[].producto_id`: exige `id` exacto, **sin** resolución por string. Si no existe ⇒ `422`/`404`.

## Vehículos
Siempre objeto `{modelo, marca, anio}` en request y response (nunca id opaco). Resolución find-or-create por la tripleta `(modelo, marca_id, anio)`.

## Reglas específicas por recurso

- **`GET /leads`** respuesta incluye `chat_id` (chat activo más reciente, join) y `estado` (derivado `ciudad→ciudades.estado_id→estados.estado`). **Nunca** aceptes `estado` en el body.
- **`GET /chats?chat_whatsapp_id=`** y **`GET /chats/{id}`** devuelven **un solo** chat (el más reciente, `created_at DESC LIMIT 1`).
- **`POST /chats`**: si el lead ya tiene chat activo, soft-delete del previo antes de crear el nuevo (un chat activo por lead).
- **`PATCH /chats/{id}`**: solo `chat_status_id` y `resumen`. Rechaza/ignora intentos de cambiar `lead_id` o `chat_whatsapp_id` (inmutables).
- **`POST /productos`** body usa `moneda_id` (Tier 1); response devuelve `"moneda": "<abreviacion>"` (string) y `precio` en MXN.
- **Todas las queries** filtran `deleted_at IS NULL`.

## Esqueleto de router

```python
# app/controllers/producto_controller.py
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from app.database import get_db

producto_router = APIRouter(prefix="/productos", tags=["productos"])

@producto_router.post("", status_code=status.HTTP_201_CREATED, response_model=ProductoOut)
def crear_producto(payload: ProductoCreate, response: Response, db: Session = Depends(get_db)):
    producto = ProductoController(db).create(payload)   # find-or-create de marca/vehiculos/categorias/ciudades
    response.headers["Location"] = f"/productos/{producto.id}"
    return producto   # precio ya en MXN, sin wrapper
```

Registra cada `*_router` en `app/main.py` con `app.include_router(...)`.

## Checklist antes de terminar
- [ ] Status correcto; POST con `Location`; sin wrapper; arrays planos.
- [ ] Errores en problem+json con `field`/`value_received` donde aplica.
- [ ] Precios convertidos a MXN; `int` centavos en toda la respuesta.
- [ ] Tier respetado por campo; normalización Tier 2 idéntica en find y create.
- [ ] find-or-create / find-or-fail correcto por campo; `productos_interes` multi-match; pre_ordenes solo por id.
- [ ] `estado`/`chat_id` derivados (no en body); chats devuelven 1; un chat activo por lead.
- [ ] Queries filtran `deleted_at IS NULL`.
