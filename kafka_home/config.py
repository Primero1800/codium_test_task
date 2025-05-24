import asyncio
import json
import logging

from aiokafka import AIOKafkaProducer, AIOKafkaClient
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import KafkaConnectionError
from fastapi.encoders import jsonable_encoder

from .settings import settings


class KafkaConfigurer:
    _producer = None
    _admin_client = None
    _lock = asyncio.Lock()
    _topics = []
    logger = logging.getLogger(__name__)

    @classmethod
    async def get_producer(cls) -> AIOKafkaProducer:
        async with cls._lock:
            if cls._producer is None:
                cls._producer = AIOKafkaProducer(
                    bootstrap_servers=settings.kafka.get_server,
                    acks=settings.kafka.KAFKA_TOPIC_ACK,
                )
                await cls._producer.start()
        return cls._producer

    @classmethod
    async def get_admin_client(cls) -> AIOKafkaAdminClient:
        async with cls._lock:
            if cls._admin_client is None:
                cls._admin_client = AIOKafkaAdminClient(
                    bootstrap_servers=settings.kafka.get_server,
                )
        return cls._admin_client

    @classmethod
    async def get_topic(cls, topic_name: str) -> str:
        topic = await cls.get_topic_name(topic_name)
        async with cls._lock:
            if  topic not in cls._topics:
                cls._topics.append(cls.create_topic_if_not_exists(topic))
        return topic

    @classmethod
    async def create_topic_if_not_exists(
            cls,
            topic: str,
            num_partitions: int = 1,
            replication_factor: int = 1
    ):
        admin_client = await cls.get_admin_client()
        await admin_client.create_topics([
            NewTopic(
                name=topic,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
            ),
        ],)

    @classmethod
    async def close_producer(cls):
        if cls._producer:
            await cls._producer.stop()
            cls._producer = None

    @classmethod
    async def close_admin_client(cls):
        if cls._admin_client:
            await cls._admin_client.stop()
            cls._admin_client = None

    @classmethod
    async def stop_kafka(cls):
        await cls.close_producer()
        await cls.close_admin_client()

    @classmethod
    async def get_topic_name(cls, topic_name: str):
        return  settings.kafka.KAFKA_TOPIC_PREFIX + '_' + topic_name

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
            return # Можно добавить retries

        try:
            message: bytes = await cls.encode_instance(instance)
        except Exception as exc:
            cls.logger.error("Error occurred while coding instance to message", exc_info=exc)
            return

        producer: AIOKafkaProducer | None = None
        try:
            producer = await cls.get_producer()
        except KafkaConnectionError as exc:
            cls.logger.error("Error occurred while establishing connection to Kafka-server", exc_info=exc)
            return # Можно добавить retries

        try:
            await producer.send_and_wait(topic, message)
        except Exception as exc:
            cls.logger.error("Error occurred while sending message to topic", exc_info=exc)
            return  # Можно добавить retries

    @classmethod
    async def encode_instance(cls, instance: dict) -> bytes:
        return json.dumps(jsonable_encoder(instance)).encode("utf-8")
