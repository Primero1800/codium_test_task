from typing import Any


class BaseErrors:
    CLASS = "Object"
    CLASS_ = CLASS + 's'
    _CLASS = CLASS_.lower()

    @classmethod
    def HANDLER_MESSAGE(cls):
        return f"Handled by {cls.CLASS} exception handler"

    @classmethod
    def DATABASE_ERROR(cls):
        return "Error occurred while changing database data"

    @classmethod
    def integrity_error_detailed(cls, exc: Any):
        return f"{cls.DATABASE_ERROR()}: {exc!r}"
