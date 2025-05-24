import asyncio
import json
import logging

from aiokafka import AIOKafkaProducer
from fastapi.encoders import jsonable_encoder

from .settings import settings


class KafkaConfigurer:
    _producer = None
    _lock = asyncio.Lock()
    logger = logging.getLogger(__name__)

    @classmethod
    async def get_producer(cls) -> AIOKafkaProducer:
        if cls._producer is None:
            async with cls._lock:
                if cls._producer is None:
                    cls._producer = AIOKafkaProducer(
                        bootstrap_servers=settings.kafka.get_server
                    )
                    await cls._producer.start()
        return cls._producer

    @classmethod
    async def close_producer(cls):
        if cls._producer:
            await cls._producer.stop()
            cls._producer = None

    @classmethod
    async def send_message(
            cls,
            instance: dict,
            topic_name: str,
    ):
        topic: str = settings.kafka.KAFKA_TOPIC_PREFIX + '_' + topic_name
        try:
            message: bytes = await cls.encode_instance(instance)
        except Exception as exc:
            cls.logger.error("Error occurred while coding instance to message", exc_info=exc)
            return
        try:
            producer: AIOKafkaProducer = await cls.get_producer()
            await producer.send_and_wait(topic, message)
        except Exception as exc:
            cls.logger.error("Error occurred while sending message to topic", exc_info=exc)

    @classmethod
    async def encode_instance(cls, instance: dict) -> bytes:
        return json.dumps(jsonable_encoder(instance)).encode("utf-8")
