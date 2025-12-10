"""Password value object."""

from __future__ import annotations

from dataclasses import dataclass

import bcrypt

from app.domain.exceptions import InvalidPasswordError

_MIN_PASSWORD_LENGTH = 8


@dataclass(frozen=True, slots=True)
class Password:
    """
    Password value object.

    Stores hashed password, never plain text.
    """

    hashed_value: str

    @classmethod
    def create(cls, plain_password: str) -> Password:
        """Create a new Password from plain text (hashes it)."""
        if not plain_password:
            msg = "Password cannot be empty"
            raise InvalidPasswordError(msg)

        if len(plain_password) < _MIN_PASSWORD_LENGTH:
            msg = f"Password must be at least {_MIN_PASSWORD_LENGTH} characters"
            raise InvalidPasswordError(msg)

        hashed = bcrypt.hashpw(
            plain_password.encode("utf-8"),
            bcrypt.gensalt(),
        )
        return cls(hashed_value=hashed.decode("utf-8"))

    @classmethod
    def from_hash(cls, hashed_value: str) -> Password:
        """Create Password from existing hash (e.g., from database)."""
        if not hashed_value:
            msg = "Hashed password cannot be empty"
            raise InvalidPasswordError(msg)
        return cls(hashed_value=hashed_value)

    def verify(self, plain_password: str) -> bool:
        """Verify a plain password against the stored hash."""
        if not plain_password:
            return False
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            self.hashed_value.encode("utf-8"),
        )
