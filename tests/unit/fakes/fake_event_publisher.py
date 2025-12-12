"""Fake event publisher for testing."""

from app.domain import DomainEvent


class FakeEventPublisher:
    """Fake event publisher that records published events."""

    def __init__(self) -> None:
        self.published_events: list[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)

    async def publish_all(self, events: list[DomainEvent]) -> None:
        self.published_events.extend(events)

    def clear(self) -> None:
        """Clear recorded events."""
        self.published_events.clear()
