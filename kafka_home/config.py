import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import KafkaConnectionError
from fastapi.encoders import jsonable_encoder

from .settings import settings


class KafkaConfigurer:
    _producer: AIOKafkaProducer | None = None
    _consumer: AIOKafkaConsumer | None = None
    # _admin_client = None
    _topics = []

    _lock_prod = asyncio.Lock()
    _lock_cons = asyncio.Lock()
    _lock_adm = asyncio.Lock()

    _cons_paused: bool = False

    logger = logging.getLogger(__name__)

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
        return cls._consumer

    # @classmethod
    # async def get_admin_client(cls) -> AIOKafkaAdminClient:
    #     async with cls._lock_adm:
    #         if cls._admin_client is None:
    #             cls._admin_client = AIOKafkaAdminClient(
    #                 bootstrap_servers=settings.kafka.get_server,
    #             )
    #         return cls._admin_client

    @classmethod
    async def get_topic(cls, topic_name: str) -> str:
        topic = await cls.get_topic_name(topic_name)
        if topic not in cls._topics:
            cls._topics.append(topic)
        return topic

    # @classmethod
    # async def create_topic_if_not_exists(
    #         cls,
    #         topic: str,
    #         num_partitions: int = 1,
    #         replication_factor: int = 1
    # ):
    #     cls.logger.warning('!!!!!!!!!!!!!!!!!!!!!!!!!!! 77')  ###########################################
    #     admin_client = await cls.get_admin_client()
    #     cls.logger.warning('!!!!!!!!!!!!!!!!!!!!!!!!!!! 79')  ###########################################
    #     await admin_client.create_topics([
    #         NewTopic(
    #             name=topic,
    #             num_partitions=num_partitions,
    #             replication_factor=replication_factor,
    #         ),
    #     ],)
    #     return topic

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

    # @classmethod
    # async def close_admin_client(cls):
    #     if cls._admin_client:
    #         await cls._admin_client.close()
    #         cls._admin_client = None

    @classmethod
    async def stop_kafka(cls):
        await cls.close_producer()
        # await cls.close_admin_client()
        await cls.close_consumer()

    @classmethod
    async def get_topic_name(cls, topic_name: str):
        return  settings.kafka.KAFKA_TOPIC_PREFIX + '-' + topic_name

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
        cls.logger.warning('?????????????? conf 157') ##################################################
        consumer: AIOKafkaConsumer | None = None
        try:
            consumer = await cls.get_consumer()
            cls.logger.warning('???????????CONSUMER??? conf 161')  ##################################################
        except KafkaConnectionError as exc:
            cls.logger.error("Error occurred while establishing connection to Kafka-server", exc_info=exc)
            return # Можно добавить retries
        cls.logger.warning('?????????????? conf 179')  ##################################################
        try:
            cls.logger.warning('???????????CONSUMER??? conf 167')  ##################################################
            message = await cls.consume_message(consumer)

            cls.logger.warning('?????????????? conf 170')  ##########################################
            cls.logger.warning(jsonable_encoder(message)) #################################
        except Exception as exc:
            cls.logger.error("Error occurred while reading message from topic", exc_info=exc)
            return  # Можно добавить retries
        cls.logger.warning('?????????????? conf 175')  ##################################################
        try:
            return await cls.decode_instance(message)
        except Exception as exc:
            cls.logger.error("Error occurred while decoding message", exc_info=exc)
            return

    @classmethod
    async def resume(cls):
        cls._cons_paused = False
        cls._consumer.resume()
        cls.logger.warning("???????????? conf 186") #############################################

    @classmethod
    async def pause(cls):
        cls._cons_paused = True
        cls._consumer.pause()
        cls.logger.warning("????????3333333333333333???? conf 192") #############################################

    @classmethod
    async def consume_message(cls, consumer: AIOKafkaConsumer):
        if cls._cons_paused:
            await cls.resume()
        try:
            cls.logger.warning("???????????? conf 199")  #############################################
            msg = await consumer.getone()
            cls.logger.warning("????????MESSAGE&&&&???? conf 201")  #############################################
            cls.logger.warning(msg)  #############################################
            await cls.pause()
            cls.logger.warning("???????????&&&&&&&&&&&&&&&&&?????? conf 204")  #############################################
            if msg:
                return msg.value
            else:
                return None
        except asyncio.CancelledError as exc:
            cls.logger.warning("Reading message cancelled:", exc_info=exc)
        except Exception as exc:
            cls.logger.warning("Error occurred while reading message:", exc_info=exc)  #############################################
            return None
