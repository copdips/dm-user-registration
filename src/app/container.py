"""Dependency injection container."""

import asyncpg
import redis.asyncio as redis

from app.application.ports.code_store import CodeStore
from app.application.ports.event_publisher import EventPublisher
from app.config import settings
from app.infrastructure.code_store.redis_code_store import RedisCodeStore
from app.infrastructure.database.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from app.infrastructure.event_publisher.console_event_publisher import (
    ConsoleEventPublisher,
)

CONTAINER_NOT_INIT_ERROR_MSG = "Container not initialized. Call init() first."


class Container:
    """dependency injection container"""

    def __init__(self) -> None:
        self._db_conn: asyncpg.Connection | None = None
        self._redis_pool: redis.ConnectionPool | None = None
        self._redis: redis.Redis | None = None
        self._code_store: CodeStore | None = None
        self._event_publisher: EventPublisher | None = None

    async def init(self) -> None:
        self._db_conn = await asyncpg.connect(settings.database_url)
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
        if self._db_conn is not None:
            await self._db_conn.close()
            self._db_conn = None
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
        if self._redis_pool is not None:
            await self._redis_pool.aclose()
            self._redis_pool = None
        self._code_store = None
        self._event_publisher = None

    @property
    def db_conn(self) -> asyncpg.Connection:
        if self._db_conn is None:
            raise RuntimeError(CONTAINER_NOT_INIT_ERROR_MSG)
        return self._db_conn

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

    def user_repository(self) -> PostgresUserRepository:
        if self._db_conn is None:
            raise RuntimeError(CONTAINER_NOT_INIT_ERROR_MSG)
        return PostgresUserRepository(self._db_conn)


container = Container()
