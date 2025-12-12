"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.container import container
from app.presentation.exception_handlers import register_exception_handlers
from app.presentation.routers.v1 import router as v1_routers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await container.init()
    print(f"======Application started: {app.title}")
    yield
    await container.close()
    print(f"=======Application stopped: {app.title}")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan,
        debug=settings.debug,
    )

    register_exception_handlers(app)
    app.include_router(v1_routers, prefix="/api")

    return app


app = create_app()
