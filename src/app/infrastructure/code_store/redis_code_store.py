"""Redis implementation of CodeStore port"""

import redis.asyncio as redis

from app.domain import Email, VerificationCode

_KEY_PREFIX = "verification_code:"


class RedisCodeStore:
    """Redis implementation of CodeStore port"""

    def __init__(self, client: redis.Redis, ttl_seconds: int = 60) -> None:
        self._client = client
        self._ttl = ttl_seconds

    def _key(self, email: Email) -> str:
        return f"{_KEY_PREFIX}{email}"

    async def save(self, email: Email, code: VerificationCode) -> None:
        await self._client.set(self._key(email), code.value, ex=self._ttl)

    async def get(self, email: Email) -> VerificationCode | None:
        value = await self._client.get(self._key(email))
        if value is None:
            return None
        return VerificationCode(str(value))

    async def delete(self, email: Email) -> None:
        await self._client.delete(self._key(email))
