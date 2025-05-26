import hashlib
import json
import logging
import redis

from functools import wraps

from src.core.settings import settings


logger = logging.getLogger(__name__)


client = redis.asyncio.Redis(
    host=settings.redis.REDIS_HOST,
    port=settings.redis.REDIS_PORT,
    db=settings.redis.REDIS_DATABASE,
)


async def get_unique_key(func, *args, **kwargs):
    if args and hasattr(args[0], '__class__'):
        args = args[1:]

    key_data = {
        'args': args,
        'kwargs': tuple(sorted(kwargs.items()))
    }
    key_json = json.dumps(key_data, default=str)
    key_hash = hashlib.sha256(key_json.encode()).hexdigest()
    return f"{settings.app.APP_NAME}:data:{func.__name__}:{key_hash}"


def cache(log_events: bool = True):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                unique_param_set = await get_unique_key(func, *args, **kwargs)
                cached_data = await client.get(unique_param_set)
                if cached_data:
                    if log_events:
                        logger.info("Getting db data from cache")
                    data = json.loads(cached_data)
                else:
                    data = await func(*args, **kwargs)
                    await client.set(
                        name=unique_param_set,
                        value=json.dumps(data),
                        ex=settings.redis.REDIS_CACHE_DB_LIFETIME_SECONDS
                    )
                return data

            except Exception as exc:
                logger.error("Error occurred while getting data from cache", exc_info=exc)
                return await func(*args, **kwargs)

        return wrapper
    return decorator
