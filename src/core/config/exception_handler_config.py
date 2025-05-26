import logging
import socket

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError

from src.tools.base_errors import BaseErrors


logger = logging.getLogger(__name__)


class Errors(BaseErrors):
    CLASS = "Application"
    UNEXPECTED_EXCEPTION = "Unexpected exception occurred"


class ExceptionHandlerConfigurer:

    simple_exceptions = [
        ValidationError,
    ]

    @staticmethod
    def add_simple_exception_handler(exc_class, app: FastAPI):
        @app.exception_handler(exc_class)
        async def simple_exception_handler(request, exc: exc_class):
            exc_argument = exc.errors() if hasattr(exc, "errors") else exc
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": jsonable_encoder(exc_argument)
                }
            )

    @staticmethod
    def config_exception_handler(app: FastAPI):

        for simple_exception in ExceptionHandlerConfigurer.simple_exceptions:
            ExceptionHandlerConfigurer.add_simple_exception_handler(
                exc_class=simple_exception,
                app=app
            )

        @app.exception_handler(socket.gaierror)
        async def database_connection_exception_handler(request, exc: socket.gaierror):
            logger.error("Unexpected exception occurred", exc_info=exc)
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": Errors.DATABASE_ERROR(),
                }
            )
