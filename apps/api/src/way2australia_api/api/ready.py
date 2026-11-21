from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from way2australia_rag.serving.readiness import Readiness

router = APIRouter(tags=["health"])


@router.get("/ready")
def get_ready(request: Request) -> JSONResponse:
    """200 `ok` or `degraded`; 503 `starting` or `failed`. The body holds state
    names and reason codes only (Spec 013 R8)."""
    readiness: Readiness = request.app.state.readiness
    snapshot = readiness.snapshot()
    body: dict[str, Any] = snapshot.to_body()
    return JSONResponse(body, status_code=snapshot.http_status)
