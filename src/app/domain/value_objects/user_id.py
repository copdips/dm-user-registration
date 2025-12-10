"""UserId value object."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from app.domain.exceptions import InvalidUserIdError


@dataclass(frozen=True, slots=True)
class UserId:
    """Strongly-typed identifier for User aggregate."""

    value: UUID

    @classmethod
    def generate(cls) -> UserId:
        """Generate a new UserId."""
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> UserId:
        """Create UserId from string representation."""
        try:
            user_id = UUID(value)
        except ValueError as e:
            msg = "Invalid UUID string"
            raise InvalidUserIdError(msg) from e
        else:
            return cls(user_id)
