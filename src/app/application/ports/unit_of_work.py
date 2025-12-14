"""Unit of Work port for DB transactions"""

from types import TracebackType
from typing import Protocol, Self

from app.application.ports.user_repository import UserRepository


class UnitOfWork(Protocol):
    """Unit of Work port for DB transactions"""

    user_repository: UserRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
