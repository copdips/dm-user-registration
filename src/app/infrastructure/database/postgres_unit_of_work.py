"""Postgres UnitOfWork implementation"""

from types import TracebackType
from typing import TYPE_CHECKING, Self

from asyncpg import Connection, Pool

from app.application.ports.unit_of_work import UnitOfWork
from app.infrastructure.database.repositories.postgres_user_repository import (
    PostgresUserRepository,
)

if TYPE_CHECKING:
    from asyncpg.transaction import Transaction


class PostgresUnitOfWork(UnitOfWork):
    """Postgres UnitOfWork implementation"""

    def __init__(self, pool: Pool) -> None:
        self._pool = pool
        self._connection: Connection | None = None
        self._transaction: Transaction | None = None
        self._user_repository: PostgresUserRepository | None = None

    @property
    def user_repository(self) -> PostgresUserRepository:
        if self._user_repository is None:
            msg = "UnitOfWork not entered. Use 'async with' context manager."
            raise RuntimeError(msg)
        return self._user_repository

    async def __aenter__(self) -> Self:
        self._connection = await self._pool.acquire()
        self._transaction = self._connection.transaction()
        await self._transaction.start()
        self._user_repository = PostgresUserRepository(self._connection)
        return self

    async def commit(self) -> None:
        if self._transaction is not None:
            await self._transaction.commit()

    async def rollback(self) -> None:
        if self._transaction is not None:
            await self._transaction.rollback()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if self._connection is not None:
                await self._pool.release(self._connection)
                self._connection = None
                self._transaction = None
                self._user_repository = None
