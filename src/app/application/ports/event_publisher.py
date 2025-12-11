"""Event publisher port."""

from typing import Protocol

from app.domain import DomainEvent


class EventPublisher(Protocol):
    """Port for publishing domain events."""

    async def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event."""
        ...

    async def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events."""
        ...
