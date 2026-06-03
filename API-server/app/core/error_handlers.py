"""Traducción de excepciones a RFC 7807 Problem Details (`application/problem+json`).

Responsabilidad de la frontera HTTP: convierte las excepciones de dominio de la capa de datos
(`core/exceptions.py`) y las de FastAPI/Starlette en respuestas tipadas con el mismo formato. Se
registra una sola vez desde `main.py` vía `register_error_handlers(app)`.

Mapeo:
- `ResolutionError`        -> 422 (+ `field`, `value_received`)   [Tier 2 find-or-fail]
- `NotFoundError`          -> 404
- `RequestValidationError` -> 422 (validación de schema de FastAPI, reformateada)
- `StarletteHTTPException` -> status original (cubre los 501 de seams/stubs y 404 de rutas)
- `Exception`              -> 500
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import NotFoundError, ResolutionError

PROBLEM_JSON = "application/problem+json"
_ERROR_TYPE_BASE = "https://api.example.com/errors/"


def _problem(
    status_code: int,
    title: str,
    detail: str,
    instance: str | None = None,
    headers: dict[str, str] | None = None,
    **extra: Any,
) -> JSONResponse:
    """Construye un body RFC 7807. Los `extra` no nulos (ej. `field`) se anexan al body.

    `headers` propaga cabeceras de la excepción original (ej. `Allow` en un 405) a la respuesta.
    """
    body: dict[str, Any] = {
        "type": f"{_ERROR_TYPE_BASE}{title.lower().replace(' ', '-')}",
        "title": title,
        "status": status_code,
        "detail": detail,
    }
    if instance is not None:
        body["instance"] = instance
    body.update({k: v for k, v in extra.items() if v is not None})
    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(body), media_type=PROBLEM_JSON, headers=headers
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ResolutionError)
    async def _resolution(request: Request, exc: ResolutionError) -> JSONResponse:
        return _problem(
            422,
            "Validation failed",
            exc.detail,
            instance=request.url.path,
            field=exc.field,
            value_received=exc.value_received,
        )

    @app.exception_handler(NotFoundError)
    async def _not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return _problem(
            status.HTTP_404_NOT_FOUND,
            "Not found",
            exc.detail,
            instance=request.url.path,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem(
            422,
            "Validation failed",
            "La petición no superó la validación de esquema",
            instance=request.url.path,
            errors=exc.errors(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Error"
        return _problem(
            exc.status_code,
            "HTTP error",
            detail,
            instance=request.url.path,
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        return _problem(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Internal server error",
            "Ocurrió un error inesperado",
            instance=request.url.path,
        )
