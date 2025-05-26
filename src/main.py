from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from src.core.settings import settings
from src.core.config import (
    AppConfigurer,
    SwaggerConfigurer,
    DBConfigurer, RateLimiter, ExceptionHandlerConfigurer,
)
from kafka_home import KafkaConfigurer
from src.api import router as router_api


@asynccontextmanager
async def lifespan(application: FastAPI):
    # startup
    yield
    # shutdown
    await KafkaConfigurer.stop_kafka()
    await DBConfigurer.dispose()


app = AppConfigurer.create_app(
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)
app.webhooks = []

app.mount("/static", StaticFiles(directory="static"), name="static")

app.openapi = AppConfigurer.get_custom_openapi(app)

# ROUTERS

app.include_router(
    router_api,
    prefix=settings.app.API_PREFIX,
)

SwaggerConfigurer.config_swagger(app, settings.app.APP_TITLE)


# comment if no need in custom exception_handler
ExceptionHandlerConfigurer.config_exception_handler(app)


######################################################################

SwaggerConfigurer.delete_router_tag(app)


# ROUTES


@app.get(
    "/",
    tags=[settings.tags.ROOT_TAG,],
)
@RateLimiter.rate_limit()
async def top(request: Request) -> str:
    return f"top here"


@app.get(
    "/kafka/",
    tags=[settings.tags.TECH_TAG,],
)
@RateLimiter.rate_limit()
async def kafka(request: Request):
    return await KafkaConfigurer.read_message()


if __name__ == "__main__":
    # uvicorn src.main:app --host 0.0.0.0 --reload
    uvicorn.run(
        app=settings.run.app_src.APP_PATH,
        host=settings.run.app_src.APP_HOST,
        port=8001,                                 # original 8000 used in uvicorn server, started from system bash
        reload=settings.run.app_src.APP_RELOAD,
    )
