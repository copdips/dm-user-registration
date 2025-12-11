"""Verification code store port."""

from typing import Protocol

from app.domain import Email, VerificationCode


class CodeStore(Protocol):
    """Port for verification code storage with TTL."""

    async def save(self, email: Email, code: VerificationCode) -> None:
        """Save verification code with TTL."""
        ...

    async def get(self, email: Email) -> VerificationCode | None:
        """Get verification code if not expired."""
        ...

    async def delete(self, email: Email) -> None:
        """Delete verification code."""
        ...
