"""Fake UnitOfWork for testing"""

from types import TracebackType
from typing import Self

from app.application.ports.unit_of_work import UnitOfWork
from tests.unit.fakes.fake_user_repository import FakeUserRepository


class FakeUnitOfWork(UnitOfWork):
    """Fake UnitOfWork for testing"""

    def __init__(self) -> None:
        self._user_repository = FakeUserRepository()
        self.committed = False
        self.rolled_back = False

    @property
    def user_repository(self) -> FakeUserRepository:
        return self._user_repository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True

    def reset(self) -> None:
        """Reset state for next test."""
        self.committed = False
        self.rolled_back = False
        self._user_repository.clear()
