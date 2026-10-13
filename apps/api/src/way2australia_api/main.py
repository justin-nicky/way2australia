from fastapi import FastAPI

from way2australia_api.api.health import router as health_router
from way2australia_api.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(
        title="Way2Australia API",
        version="0.1.0",
        description="AI-powered NAATI CCL preparation platform",
        debug=app_settings.app_debug,
    )
    app.state.settings = app_settings

    # Register routers
    app.include_router(health_router)

    return app


app = create_app()
