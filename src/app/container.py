"""Dependency injection container."""

import asyncpg

from app.config import settings
from app.infrastructure.code_store.memory_code_store import MemoryCodeStore
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
        self._code_store: MemoryCodeStore | None = None
        self._event_publisher: ConsoleEventPublisher | None = None

    async def init(self) -> None:
        self._db_conn = await asyncpg.connect(settings.database_url)

        self._code_store = MemoryCodeStore(
            ttl_seconds=settings.verification_code_ttl_seconds
        )

        self._event_publisher = ConsoleEventPublisher(self._code_store)

    async def close(self) -> None:
        if self._db_conn is not None:
            await self._db_conn.close()
            self._db_conn = None

    @property
    def db_conn(self) -> asyncpg.Connection:
        if self._db_conn is None:
            raise RuntimeError(CONTAINER_NOT_INIT_ERROR_MSG)
        return self._db_conn

    @property
    def code_store(self) -> MemoryCodeStore:
        if self._code_store is None:
            raise RuntimeError(CONTAINER_NOT_INIT_ERROR_MSG)
        return self._code_store

    @property
    def event_publisher(self) -> ConsoleEventPublisher:
        if self._event_publisher is None:
            raise RuntimeError(CONTAINER_NOT_INIT_ERROR_MSG)
        return self._event_publisher

    def user_repository(self) -> PostgresUserRepository:
        if self._db_conn is None:
            raise RuntimeError(CONTAINER_NOT_INIT_ERROR_MSG)
        return PostgresUserRepository(self._db_conn)


container = Container()
