"""Fake user repository for testing."""

from app.domain import Email, User, UserId


class FakeUserRepository:
    """In-memory fake repository for testing."""

    def __init__(self) -> None:
        self._users: dict[UserId, User] = {}

    async def get_by_id(self, user_id: UserId) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: Email) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def save(self, user: User) -> None:
        self._users[user.id] = user

    def clear(self) -> None:
        """Clear all users (for test cleanup)."""
        self._users.clear()
