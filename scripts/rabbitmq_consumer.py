"""RabbitMQ consumer."""

import asyncio
import json
import signal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rabbitmq_amqp_python_client import (
    AddressHelper,
    AMQPMessagingHandler,
    AsyncEnvironment,
    ConnectionClosed,
    Converter,
    Event,
    ExchangeSpecification,
    ExchangeToQueueBindingSpecification,
    ExchangeType,
    QuorumQueueSpecification,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    rabbitmq_url: str = Field(default=...)
    rabbitmq_exchange_name: str = Field(default=...)
    rabbitmq_queue_name: str = Field(default=...)
    rabbitmq_routing_key: str = Field(default=...)
    rabbitmq_retry_seconds: int = Field(default=2)


settings = Settings()


class MyMessageHandler(AMQPMessagingHandler):
    def __init__(self):
        super().__init__()

    def on_amqp_message(self, event: Event):
        message_dict = json.loads(Converter.bytes_to_string(event.message.body))
        print(f"Received message: {message_dict}")
        self.delivery_context.accept(event)


async def declare_topology(
    management,
    *,
    exchange_name: str,
    queue_name: str,
    routing_key: str,
):
    await management.declare_exchange(
        ExchangeSpecification(name=exchange_name, exchange_type=ExchangeType.topic)
    )
    await management.declare_queue(
        QuorumQueueSpecification(name=queue_name)
        # QuorumQueueSpecification(name=queue_name, dead_letter_exchange="dead-letter")
    )
    await management.bind(
        ExchangeToQueueBindingSpecification(
            source_exchange=exchange_name,
            destination_queue=queue_name,
            binding_key=routing_key,
        )
    )


def _install_sigint_handler(stop_event: asyncio.Event) -> asyncio.AbstractEventLoop:
    loop = asyncio.get_running_loop()

    def handle_sigint():
        print("\nCtrl+C detected, stopping consumer gracefully...")
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, handle_sigint)
    return loop


async def consume_messages(connection, queue_name: str) -> bool:
    addr_queue = AddressHelper.queue_address(queue_name)
    handler = MyMessageHandler()
    stop_event = asyncio.Event()

    async with await connection.consumer(
        addr_queue, message_handler=handler
    ) as consumer:
        loop = _install_sigint_handler(stop_event)
        try:
            consumer_task = asyncio.create_task(consumer.run())
            stop_task = asyncio.create_task(stop_event.wait())

            done, _pending = await asyncio.wait(
                {consumer_task, stop_task},
                return_when=asyncio.FIRST_COMPLETED,
            )

            if consumer_task in done:
                await consumer_task
                stop_event.set()
            else:
                await stop_event.wait()

            print("Stopping consumer...")
            await consumer.stop_processing()
            try:
                await asyncio.wait_for(consumer_task, timeout=3.0)
            except TimeoutError:
                print("Consumer task timed out")
        finally:
            loop.remove_signal_handler(signal.SIGINT)
    return stop_event.is_set()


async def main() -> None:
    exchange_name = settings.rabbitmq_exchange_name
    queue_name = settings.rabbitmq_queue_name
    routing_key = settings.rabbitmq_routing_key

    while True:
        try:
            async with (
                AsyncEnvironment(uri=settings.rabbitmq_url) as environment,
                await environment.connection() as connection,
                await connection.management() as management,
            ):
                await declare_topology(
                    management,
                    exchange_name=exchange_name,
                    queue_name=queue_name,
                    routing_key=routing_key,
                )

                print("RabbitMQ consumer is running - press `CTRL + C` to terminate.")
                stopped_by_signal = await consume_messages(connection, queue_name)
                if stopped_by_signal:
                    break
        except ConnectionClosed:
            print(
                f"Connection closed, retrying in {settings.rabbitmq_retry_seconds} seconds..."
            )
            await asyncio.sleep(settings.rabbitmq_retry_seconds)
        except Exception as exc:  # noqa: BLE001 blind-except
            print(
                f"Unexpected consumer error: {exc}, "
                f"retrying in {settings.rabbitmq_retry_seconds} seconds..."
            )
            await asyncio.sleep(settings.rabbitmq_retry_seconds)
            continue


if __name__ == "__main__":
    asyncio.run(main())
