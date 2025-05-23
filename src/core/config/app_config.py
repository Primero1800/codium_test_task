import logging

from typing import Callable, Dict, Any
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse

from src.core.settings import settings


class AppConfigurer:
    logging.basicConfig(
        level=settings.logging.log_level_value,
        format=settings.logging.LOGGING_FORMAT,
    )

    @staticmethod
    def create_app(docs_url, redoc_url, lifespan) -> FastAPI:
        app = FastAPI(
            default_response_class=ORJSONResponse,
            lifespan=lifespan,
            docs_url=docs_url,
            redoc_url=redoc_url,
        )
        return app

    @staticmethod
    def get_custom_openapi(subject: FastAPI) -> Callable[[], Dict[str, Any]]:
        def custom_openapi() -> Dict[str, Any]:
            if subject.openapi_schema:
                return subject.openapi_schema
            openapi_schema = get_openapi(
                title=settings.app.APP_TITLE,
                version=settings.app.APP_VERSION,
                description=settings.app.APP_DESCRIPTION,
                routes=subject.routes,
                webhooks=subject.webhooks,
            )
            subject.openapi_schema = openapi_schema
            return subject.openapi_schema

        return custom_openapi
