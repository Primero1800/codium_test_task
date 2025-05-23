from typing import Any


class Errors:
    CLASS = "Request"
    _CLASS = "requests"

    @classmethod
    def HANDLER_MESSAGE(cls):
        return f"Handled by {cls.CLASS}s exception handler"

    @classmethod
    def DATABASE_ERROR(cls):
        return "Error occurred while changing database data"

    @classmethod
    def integrity_error_detailed(cls, exc: Any):
        return f"{cls.DATABASE_ERROR()}: {exc!r}"
