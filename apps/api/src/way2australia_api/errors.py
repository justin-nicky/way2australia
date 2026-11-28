"""Exception handlers and error bodies (Spec 013 R9, R12, R13).

Bodies hold a request ID, an error code and field locations; never the input,
a client message, a path or a key. A validation error drops FastAPI's `input`
and `ctx`, so a query is never echoed.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from way2australia_api.middleware import fake_headers

logger = logging.getLogger(__name__)


def request_id_of(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def error_response(
    request: Request,
    status: int,
    error: str,
    *,
    headers: dict[str, str] | None = None,
    **extra: Any,
) -> JSONResponse:
    request_id = request_id_of(request)
    merged = {**fake_headers(request.scope), **(headers or {})}
    if request_id is not None:
        merged["X-Request-ID"] = request_id
    return JSONResponse(
        {"request_id": request_id, "error": error, **extra},
        status_code=status,
        headers=merged,
    )


def invalid_request(fields: list[dict[str, Any]]) -> dict[str, Any]:
    return {"fields": fields}


async def _validation_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    fields = [
        {"loc": [str(part) for part in e["loc"]], "msg": str(e["msg"])}
        for e in exc.errors()
    ]
    return error_response(request, 422, "invalid_request", fields=fields)


async def _internal_handler(request: Request, exc: Exception) -> JSONResponse:
    # request ID and class only: no exc_info, no message
    logger.error(
        "request failed: request_id=%s error=%s",
        request_id_of(request),
        type(exc).__name__,
    )
    return error_response(request, 500, "internal_error")


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, _validation_handler)
    app.add_exception_handler(Exception, _internal_handler)
