from collections.abc import Callable

from fastapi import FastAPI
from way2australia_rag.serving.readiness import Readiness

from way2australia_api.api.answer import router as answer_router
from way2australia_api.api.health import router as health_router
from way2australia_api.api.ready import router as ready_router
from way2australia_api.config import Settings, get_settings
from way2australia_api.errors import install_error_handlers
from way2australia_api.lifespan import StackFactory, make_lifespan
from way2australia_api.logs import configure_logging
from way2australia_api.middleware import BodySizeMiddleware, RequestIdMiddleware


def create_app(
    settings: Settings | None = None,
    *,
    stack_factory: StackFactory | None = None,
    on_fatal: Callable[[], None] | None = None,
) -> FastAPI:
    """`stack_factory` and `on_fatal` are test seams: the factory replaces
    `open_serving_stack` in phase 2, `on_fatal` replaces the process exit."""
    app_settings = settings or get_settings()
    configure_logging()
    app = FastAPI(
        title="Way2Australia API",
        version="0.1.0",
        description="AI-powered NAATI CCL preparation platform",
        debug=app_settings.app_debug,
        lifespan=make_lifespan(
            app_settings, stack_factory=stack_factory, on_fatal=on_fatal
        ),
    )
    app.state.settings = app_settings
    app.state.readiness = Readiness(fake=app_settings.api_fake)

    # The request ID middleware is outermost so every response carries the ID.
    app.add_middleware(BodySizeMiddleware)
    app.add_middleware(RequestIdMiddleware)
    install_error_handlers(app)

    # Register routers
    app.include_router(health_router)
    app.include_router(ready_router)
    app.include_router(answer_router)

    return app


app = create_app()
