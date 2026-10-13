from fastapi.testclient import TestClient
from way2australia_api.main import create_app


def test_create_app() -> None:
    app = create_app()

    assert app.title == "Way2Australia API"


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
