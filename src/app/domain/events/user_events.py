"""User domain events."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.value_objects.email import Email
from app.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent:
    """Base class for all domain events."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True, kw_only=True)
class UserRegistered(DomainEvent):
    """Event raised when a new user registers."""

    user_id: UserId
    email: Email


@dataclass(frozen=True, slots=True, kw_only=True)
class UserActivated(DomainEvent):
    """Event raised when a user activates their account."""

    user_id: UserId
    email: Email
