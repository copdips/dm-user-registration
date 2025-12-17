from collections.abc import AsyncGenerator
from unittest.mock import Mock

import asyncpg
import pytest
import redis.asyncio as redis
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.container import container
from app.infrastructure.event_publisher.rabbitmq_event_publisher import (
    RabbitMQEventPublisher,
)
from app.main import app


@pytest.fixture(scope="session", autouse=True)
async def reset_postgres() -> None:
    conn = await asyncpg.connect(settings.database_url)
    try:
        await conn.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE;")
    finally:
        await conn.close()


@pytest.fixture(scope="session", autouse=True)
async def reset_redis() -> None:
    client = redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )
    try:
        await client.flushdb()
    finally:
        await client.aclose()


@pytest.fixture(scope="session", autouse=True)
async def reset_rabbitmq() -> None:
    publisher = RabbitMQEventPublisher(
        settings.rabbitmq_url,
        settings.rabbitmq_exchange_name,
        settings.rabbitmq_queue_name,
        settings.rabbitmq_routing_key,
        Mock(),
    )
    await publisher.connect()
    try:
        await publisher.purge_queue()
    finally:
        await publisher.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient]:
    await container.init()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test/api",
    ) as client:
        yield client
    await container.close()
