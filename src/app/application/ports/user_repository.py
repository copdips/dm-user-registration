"""User repository port."""

from typing import Protocol

from app.domain import Email, User, UserId


class UserRepository(Protocol):
    """Port for user persistence."""

    async def get_by_id(self, user_id: UserId) -> User | None:
        """Get user by ID."""
        ...

    async def get_by_email(self, email: Email) -> User | None:
        """Get user by email."""
        ...

    async def save(self, user: User) -> None:
        """Save user."""
        ...
