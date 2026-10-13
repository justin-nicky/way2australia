from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, status_code=200)
def get_health() -> HealthResponse:
    return HealthResponse(status="ok")
