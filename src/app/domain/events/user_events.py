"""User domain events."""

from dataclasses import dataclass

from app.domain.events.base import DomainEvent
from app.domain.value_objects.email import Email
from app.domain.value_objects.user_id import UserId


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
