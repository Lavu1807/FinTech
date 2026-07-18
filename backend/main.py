"""
Application entry point for FinSight AI.
"""

from fastapi import FastAPI
from backend.config.settings import settings
from backend.utils.logger import logger
from backend.api.middlewares import setup_middlewares
from backend.api.exceptions import setup_exception_handlers
from backend.api.v1.router import api_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(
            f"Starting {settings.PROJECT_NAME} in {settings.APP_ENV.value} mode."
        )
        logger.info(f"API available at {settings.API_V1_STR}")

        # Validate Directories
        settings.uploads_dir.mkdir(parents=True, exist_ok=True)
        settings.workflows_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Verified export directories at {settings.EXPORTS_DIR}")

        # Validate API Key for Production
        if settings.APP_ENV == "production":
            provider = getattr(settings, "LLM_PROVIDER", "mistral").lower()
            if provider == "mistral" and not getattr(settings, "MISTRAL_API_KEY", None):
                logger.error(
                    "CRITICAL: MISTRAL_API_KEY is missing in production environment!"
                )
                raise RuntimeError("Missing MISTRAL_API_KEY in production.")
        yield

    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="Multi-Agent Financial Intelligence Copilot API",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # 1. Register Middlewares
    setup_middlewares(app)

    # 2. Register Exception Handlers
    setup_exception_handlers(app)

    # 3. Register API Routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
