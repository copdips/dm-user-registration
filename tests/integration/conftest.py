from collections.abc import AsyncGenerator

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.container import container
from app.main import app


@pytest.fixture(scope="session", autouse=True)
async def reset_postgres() -> None:
    conn = await asyncpg.connect(settings.database_url)
    try:
        await conn.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE;")
    finally:
        await conn.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient]:
    await container.init()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test/api",
    ) as client:
        yield client
    await container.close()
