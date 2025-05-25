from src.tools.base_errors import BaseErrors


class Errors(BaseErrors):
    CLASS = "Kafka"

    @classmethod
    def NO_INSTANCES_AVAILABLE(cls, instance: str):
        return f"No new {instance} available"
