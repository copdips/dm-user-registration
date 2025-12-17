"""RabbitMQ implementation of EventPublisher port."""

import asyncio
import json
from typing import Any

from rabbitmq_amqp_python_client import (
    AddressHelper,
    AsyncConnection,
    AsyncEnvironment,
    AsyncManagement,
    AsyncPublisher,
    ConnectionClosed,
    Converter,
    ExchangeSpecification,
    ExchangeToQueueBindingSpecification,
    ExchangeType,
    Message,
    QuorumQueueSpecification,
)

from app.application.exceptions import VerificationCodeExpiredError
from app.application.ports.code_store import CodeStore
from app.domain import (
    DomainEvent,
    UserActivated,
    UserNewVerificationCodeCreated,
    UserRegistered,
)


class RabbitMQEventPublisher:
    """
    RabbitMQ implementation of EventPublisher port.
    """

    def __init__(
        self,
        url: str,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        retry_seconds: int,
        code_store: CodeStore,
    ) -> None:
        self._rabbitmq_url = url
        self._exchange_name = exchange_name
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._retry_seconds = retry_seconds
        self._code_store: CodeStore = code_store
        self._environment: AsyncEnvironment = None
        self._connection: AsyncConnection = None
        self._management: AsyncManagement = None
        self.bind_name: str = None
        self.addr: str = None
        self._publisher: AsyncPublisher = None

    async def connect(self):
        self._environment = AsyncEnvironment(uri=self._rabbitmq_url)
        self._connection = await self._environment.connection()
        await self._connection.dial()
        self._management = await self._connection.management()
        await self._management.declare_exchange(
            ExchangeSpecification(
                name=self._exchange_name, exchange_type=ExchangeType.topic
            )
        )
        await self._management.declare_queue(
            QuorumQueueSpecification(name=self._queue_name)
        )
        self.bind_name = await self._management.bind(
            ExchangeToQueueBindingSpecification(
                source_exchange=self._exchange_name,
                destination_queue=self._queue_name,
                binding_key=self._routing_key,
            )
        )
        self.addr = AddressHelper.exchange_address(
            self._exchange_name, self._routing_key
        )
        self._publisher = await self._connection.publisher(self.addr)

    async def close(self) -> None:
        await self._publisher.close()
        await self._management.unbind(self.bind_name)
        await self._management.close()
        await self._connection.close()
        await self._environment.close()

    async def publish(self, event: DomainEvent) -> None:
        message_str = await self._serialize_event(event)
        # print("Publishing message:", message_str)
        try:
            await self._publisher.publish(
                Message(
                    body=Converter.string_to_bytes(message_str),
                )
            )
        except ConnectionClosed:
            await asyncio.sleep(self._retry_seconds)
            await self.connect()
            await self._publisher.publish(
                Message(
                    body=Converter.string_to_bytes(message_str),
                )
            )

    async def publish_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)

    async def _serialize_event(self, event: DomainEvent) -> str:
        data: dict[str, Any] = {
            "event_type": type(event).__name__,
            "event_id": str(event.event_id),
            "occurred_at": event.occurred_at.isoformat(),
            "payload": {},
        }

        match event:
            case (
                UserRegistered(user_id=uid, email=email)
                | UserNewVerificationCodeCreated(user_id=uid, email=email)
            ):
                code = await self._code_store.get(email)
                if code is None:
                    raise VerificationCodeExpiredError(email.value)
                data["payload"] = {
                    "user_id": str(uid.value),
                    "email": email.value,
                    "code": code.value,
                }
            case UserActivated(user_id=uid, email=email):
                data["payload"] = {
                    "user_id": str(uid.value),
                    "email": email.value,
                }
            case _:
                print(f"Unhandled event type: {type(event)}")

        return json.dumps(data)

    async def purge_queue(self) -> None:
        if self._management is None:
            msg = "RabbitMQ not connected. Call connect() first."
            raise RuntimeError(msg)
        await self._management.purge_queue(self._queue_name)
