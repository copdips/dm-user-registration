"""VerificationCode value object."""

from __future__ import annotations

import secrets
from dataclasses import dataclass

from app.domain.exceptions import InvalidVerificationCodeError

_CODE_LENGTH = 4


@dataclass(frozen=True, slots=True)
class VerificationCode:
    """
    Verification code value object.

    4-digit numeric code for email verification.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            msg = "Verification code cannot be empty"
            raise InvalidVerificationCodeError(msg)

        if not self.value.isdigit():
            msg = "Verification code must be numeric"
            raise InvalidVerificationCodeError(msg)

        if len(self.value) != _CODE_LENGTH:
            msg = f"Verification code must be {_CODE_LENGTH} digits"
            raise InvalidVerificationCodeError(msg)

    @classmethod
    def generate(cls) -> VerificationCode:
        """Generate a new random 4-digit code."""
        code = f"{secrets.randbelow(10_000):04d}"
        return cls(code)

    def matches(self, other: str) -> bool:
        """Check if the provided code matches."""
        return secrets.compare_digest(self.value, other)
