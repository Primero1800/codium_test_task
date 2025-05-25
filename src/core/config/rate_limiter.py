import hashlib
import json
import logging
import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Any

from fastapi import Request, status
from fastapi.responses import ORJSONResponse

from src.core.settings import settings


logger = logging.getLogger(__name__)

InMemoryStorage = {}


class StorageGateway:
    def __init__(self, storage: Any):
        self.storage = storage

    async def get(self, key: str):
        return self.storage.get(key)

    async def set(self, key: str, value: Any, ex: int | None = None):
        if isinstance(self.storage, dict):
            self.storage[key] = value
        else:
            # ex=settings.redis.REDIS_CACHE_LIFETIME_SECONDS
            self.storage.set(key, value, ex=ex)


@contextmanager
def storage_context(use_redis: bool = False):
    if use_redis:
        yield 'redis_client_placeholder'
    else:
        yield StorageGateway(InMemoryStorage)


class RateLimiter:

    @staticmethod
    def rate_limit(
            max_calls: int = settings.rate_limiter.RATE_LIMITER_CALLS,
            period: int = settings.rate_limiter.RATE_LIMITER_PERIOD,
    ):
        def decorator(
                func: Callable[[Request, Any], Any]
        ) -> Callable[[Request, Any], Any]:

            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs) -> Any:
                if not request.client:
                    logger.warning("Request has no client information")
                    return ORJSONResponse(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        content={
                            "message": "Handled by Rate Limiter exception handler",
                            "detail": "Request has no client information",
                        }
                    )

                ip_address: str = request.client.host
                unique_id: str = hashlib.sha256(ip_address.encode()).hexdigest()
                now = time.time()

                with storage_context() as client:
                    storage_key = f"{settings.app.APP_NAME}_rate_limit:{unique_id}"
                    timestamps = await client.get(storage_key)
                    if timestamps is None:
                        timestamps = []
                    else:
                        timestamps = json.loads(timestamps)

                    timestamps = [t for t in timestamps if now - t < period]

                    if len(timestamps) < max_calls:
                        timestamps.append(now)
                        await client.set(
                            storage_key,
                            json.dumps(timestamps),
                        )
                        return await func(request, *args, **kwargs)

                wait: float = period - (now - timestamps[0])
                logger.warning("Too many requests from %r" % request.client.host)
                return ORJSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "message": "Handled by Rate Limiter exception handler",
                        "detail": f"Rate limit exceed. Retry after {wait:.2f} seconds",
                    }
                )

            return wrapper

        return decorator
