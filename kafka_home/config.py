import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

from .settings import settings
from .exceptions import Errors


class KafkaConfigurer:
    _producer: AIOKafkaProducer | None = None
    _consumer: AIOKafkaConsumer | None = None
    _topics: list = []

    _lock_prod: asyncio.Lock = asyncio.Lock()
    _lock_cons: asyncio.Lock = asyncio.Lock()

    _cons_paused: bool = False

    logger: logging.Logger = logging.getLogger(__name__)

    @classmethod
    async def get_producer(cls) -> AIOKafkaProducer:
        async with cls._lock_prod:
            if cls._producer is None:
                cls._producer = AIOKafkaProducer(
                    bootstrap_servers=settings.kafka.get_server,
                    acks=settings.kafka.KAFKA_TOPIC_ACK,
                )
                await cls._producer.start()
            return cls._producer

    @classmethod
    async def get_consumer(cls) -> AIOKafkaConsumer:
        async with cls._lock_cons:
            if cls._consumer is None:
                cls._consumer = AIOKafkaConsumer(
                    *cls._topics,
                    bootstrap_servers=settings.kafka.get_server,
                    auto_offset_reset='earliest'
                )
                await cls._consumer.start()
            else:
                current_subs = cls._consumer.subscription()
                if set(current_subs) != set(cls._topics):
                    cls._consumer.unsubscribe()
                    cls._consumer.subscribe(cls._topics)
        return cls._consumer

    @classmethod
    async def get_topic(cls, topic_name: str) -> str:
        topic = await cls.get_topic_name(topic_name)
        if topic not in cls._topics:
            cls._topics.append(topic)
        return topic

    @classmethod
    async def close_producer(cls):
        if cls._producer:
            await cls._producer.stop()
            cls._producer = None

    @classmethod
    async def close_consumer(cls):
        if cls._consumer:
            await cls._consumer.stop()
            cls._consumer = None

    @classmethod
    async def stop_kafka(cls):
        await cls.close_producer()
        await cls.close_consumer()

    @classmethod
    async def get_topic_name(cls, topic_name: str):
        return settings.kafka.KAFKA_TOPIC_PREFIX + '-' + topic_name

    @classmethod
    async def send_message(
            cls,
            instance: dict,
            topic_name: str,
    ):
        try:
            topic = await cls.get_topic(topic_name)
        except Exception as exc:
            cls.logger.error("Error occurred while creating topic", exc_info=exc)
            return  # Можно добавить retries

        try:
            message: bytes = await cls.encode_instance(instance)
        except Exception as exc:
            cls.logger.error("Error occurred while coding instance to message", exc_info=exc)
            return

        try:
            producer: AIOKafkaProducer = await cls.get_producer()
        except KafkaConnectionError as exc:
            cls.logger.error("Error occurred while establishing connection to Kafka-server", exc_info=exc)
            return  # Можно добавить retries

        try:
            result = await producer.send_and_wait(topic=topic, value=message)
            cls.logger.warning(jsonable_encoder(result))
            return result
        except Exception as exc:
            cls.logger.error("Error occurred while sending message to topic", exc_info=exc)
            return  # Можно добавить retries

    @classmethod
    async def encode_instance(cls, instance: dict) -> bytes:
        return json.dumps(jsonable_encoder(instance)).encode("utf-8")

    @classmethod
    async def decode_instance(cls, message: Any) -> dict:
        return json.loads(message.decode("utf-8"))

    @classmethod
    async def read_message(cls):
        try:
            consumer: AIOKafkaConsumer = await cls.get_consumer()
        except KafkaConnectionError as exc:
            cls.logger.error("Error occurred while establishing connection to Kafka-server", exc_info=exc)
            return  # Можно добавить retries
        try:
            message = await cls.consume_message(consumer)
        except Exception as exc:
            cls.logger.error("Error occurred while reading message from topic", exc_info=exc)
            return  # Можно добавить retries
        if not message:
            return ORJSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": Errors.NO_INSTANCES_AVAILABLE("messages")
                }
            )
        try:
            return await cls.decode_instance(message)
        except Exception as exc:
            cls.logger.error("Error occurred while decoding message", exc_info=exc)
            return

    @classmethod
    async def resume(cls):
        cls._cons_paused = False
        cls._consumer.resume()

    @classmethod
    async def pause(cls):
        cls._cons_paused = True
        cls._consumer.pause()

    @classmethod
    async def consume_message(cls, consumer: AIOKafkaConsumer):
        msg: Any = None
        if cls._cons_paused:
            await cls.resume()
        try:
            msg = await cls.get_one_or_none(consumer)
            await cls.pause()
        except asyncio.CancelledError as exc:
            cls.logger.warning("Reading message cancelled:", exc_info=exc)
        except TimeoutError as exc:
            cls.logger.warning("Error occurred while reading message:", exc_info=exc)
        finally:
            return msg.value if msg else None

    @classmethod
    async def get_one_or_none(cls, consumer: AIOKafkaConsumer):
        return await asyncio.wait_for(
            consumer.getone(),
            timeout=settings.kafka.KAFKA_CONSUMER_TIMEOUT,
        )
