from pathlib import Path

from src.tools.base_custom_settings import BaseCustomSettings


# .
BASE_DIR = Path(__file__).resolve().parent


class CustomSettings(BaseCustomSettings):
    pass


CustomSettings.set_app_base(BASE_DIR)


class KafkaSettings(CustomSettings):
    KAFKA_SERVER_HOST: str
    KAFKA_SERVER_PORT: int
    KAFKA_TOPIC_PREFIX: str
    KAFKA_TOPIC_ACK: str
    KAFKA_NUM_PARTITIONS: int
    KAFKA_REPLICATION_FACTOR: int
    KAFKA_CONSUMER_TIMEOUT: int = 3

    @property
    def get_server(self) -> str:
        return f"{self.KAFKA_SERVER_HOST}:{self.KAFKA_SERVER_PORT}"


class Settings(CustomSettings):
    kafka: KafkaSettings = KafkaSettings()


settings = Settings()
