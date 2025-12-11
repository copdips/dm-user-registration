"""User entity - Aggregate Root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.domain.events.user_events import UserActivated, UserRegistered
from app.domain.exceptions import UserAlreadyActiveError
from app.domain.value_objects.user_id import UserId

if TYPE_CHECKING:
    from app.domain.events.base import DomainEvent
    from app.domain.value_objects.email import Email
    from app.domain.value_objects.password import Password


@dataclass(slots=True)
class User:
    """
    User Aggregate Root.

    Represents a user account with email verification.
    """

    id: UserId
    email: Email
    password: Password
    is_active: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    @classmethod
    def create(cls, email: Email, password: Password) -> User:
        """Factory method to create a new user."""
        user_id = UserId.generate()
        user = cls(
            id=user_id,
            email=email,
            password=password,
            is_active=False,
        )
        user._record_event(UserRegistered(user_id=user_id, email=email))
        return user

    def activate(self) -> None:
        """Activate the user account."""
        if self.is_active:
            msg = "User is already active"
            raise UserAlreadyActiveError(msg)

        self.is_active = True
        self._record_event(UserActivated(user_id=self.id, email=self.email))

    def verify_password(self, plain_password: str) -> bool:
        """Verify if the provided password matches."""
        return self.password.verify(plain_password)

    def _record_event(self, event: DomainEvent) -> None:
        """Record a domain event."""
        self._events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        """Collect and clear pending domain events."""
        events = self._events.copy()
        self._events.clear()
        return events
