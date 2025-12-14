"""Dependency injection container."""

import asyncpg
import redis.asyncio as redis

from app.application.ports.code_store import CodeStore
from app.application.ports.event_publisher import EventPublisher
from app.config import settings
from app.infrastructure.code_store.redis_code_store import RedisCodeStore
from app.infrastructure.database.postgres_unit_of_work import PostgresUnitOfWork
from app.infrastructure.event_publisher.console_event_publisher import (
    ConsoleEventPublisher,
)

CONTAINER_NOT_INIT_ERROR_MSG = "Container not initialized. Call init() first."


class Container:
    """dependency injection container"""

    def __init__(self) -> None:
        self._db_pool: asyncpg.Pool | None = None
        self._redis_pool: redis.ConnectionPool | None = None
        self._redis: redis.Redis | None = None
        self._code_store: CodeStore | None = None
        self._event_publisher: EventPublisher | None = None

    async def init(self) -> None:
        self._db_pool = await asyncpg.create_pool(dsn=settings.database_url)
        self._redis_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
        )
        self._redis = redis.Redis.from_pool(self._redis_pool)

        self._code_store = RedisCodeStore(
            self._redis, ttl_seconds=settings.verification_code_ttl_seconds
        )

        self._event_publisher = ConsoleEventPublisher(self._code_store)

    async def close(self) -> None:
        if self._db_pool is not None:
            await self._db_pool.close()
            self._db_pool = None
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
        if self._redis_pool is not None:
            await self._redis_pool.aclose()
            self._redis_pool = None
        self._code_store = None
        self._event_publisher = None

    @property
    def db_pool(self) -> asyncpg.Pool:
        if self._db_pool is None:
            raise RuntimeError(CONTAINER_NOT_INIT_ERROR_MSG)
        return self._db_pool

    @property
    def code_store(self) -> CodeStore:
        if self._code_store is None:
            raise RuntimeError(CONTAINER_NOT_INIT_ERROR_MSG)
        return self._code_store

    @property
    def event_publisher(self) -> EventPublisher:
        if self._event_publisher is None:
            raise RuntimeError(CONTAINER_NOT_INIT_ERROR_MSG)
        return self._event_publisher

    def uow(self) -> PostgresUnitOfWork:
        if self._db_pool is None:
            raise RuntimeError(CONTAINER_NOT_INIT_ERROR_MSG)
        return PostgresUnitOfWork(self._db_pool)


container = Container()
