from fastapi import FastAPI

from way2australia_api.api.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Way2Australia API",
        version="0.1.0",
        description="AI-powered NAATI CCL preparation platform",
    )

    # Register routers
    app.include_router(health_router)

    return app


app = create_app()
