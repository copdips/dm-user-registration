"""Fake code store for testing."""

from app.domain import Email, VerificationCode


class FakeCodeStore:
    """In-memory fake code store for testing (no TTL)."""

    def __init__(self) -> None:
        self._codes: dict[str, VerificationCode] = {}

    async def save(self, email: Email, code: VerificationCode) -> None:
        self._codes[email.value] = code

    async def get(self, email: Email) -> VerificationCode | None:
        return self._codes.get(email.value)

    async def delete(self, email: Email) -> None:
        self._codes.pop(email.value, None)

    def clear(self) -> None:
        """Clear all codes (for test cleanup)."""
        self._codes.clear()
