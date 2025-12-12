"""Console implementation of EventPublisher port."""

from app.domain import (
    DomainEvent,
    UserActivated,
    UserNewVerificationCodeCreated,
    UserRegistered,
)
from app.infrastructure.code_store.memory_code_store import MemoryCodeStore


class ConsoleEventPublisher:
    """
    Console implementation of EventPublisher port.
    """

    def __init__(self, code_store: MemoryCodeStore) -> None:
        self._code_store: MemoryCodeStore = code_store

    async def publish(self, event: DomainEvent) -> None:
        if isinstance(event, (UserRegistered, UserNewVerificationCodeCreated)):
            code = await self._code_store.get(event.email)
            print(f"Sending to email {event.email} with verification code: {code}")

        elif isinstance(event, UserActivated):
            print(f"User {event.email} has been activated.")

        else:
            print(f"Unhandled event type: {type(event)}")

    async def publish_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
