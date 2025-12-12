"""In-memory implementation of CodeStore port."""

import time

from app.domain import Email, VerificationCode


class MemoryCodeStore:
    """
    In-memory implementation of CodeStore port.
    """

    def __init__(self, ttl_seconds: int = 60) -> None:
        self._store: dict[str, tuple[VerificationCode, float]] = {}
        self._ttl = ttl_seconds

    async def save(self, email: Email, code: VerificationCode) -> None:
        expires_at = time.time() + self._ttl
        self._store[email.value] = (code, expires_at)

    async def get(self, email: Email) -> VerificationCode | None:
        entry = self._store.get(email.value)
        if entry is None:
            return None

        code, expires_at = entry
        if time.time() > expires_at:
            del self._store[email.value]
            return None

        return code

    async def delete(self, email: Email) -> None:
        self._store.pop(email.value, None)
