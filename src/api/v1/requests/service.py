import logging
from typing import Optional, TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from src.tools.redis_cache_decorator import cache
from .repository import Repository
from .schemas import RequestCreate, RequestRead
from .exceptions import Errors

from kafka_home import KafkaConfigurer

if TYPE_CHECKING:
    from .filters import RequestFilter


CLASS = "Request"


logger = logging.Logger(__name__)


class Service:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logger

    @cache(log_events=True)
    async def get_all(
            self,
            filter_model: Optional["RequestFilter"] = None,
            page: Optional[int] = 1,
            size: Optional[int] = 10,
    ):
        repository: Repository = Repository(
            session=self.session
        )
        return await repository.get_all(
            filter_model=filter_model,
            page=page,
            size=size,
        )

    async def create_one(
            self,
            instance: RequestCreate
    ):
        repository: Repository = Repository(
            session=self.session
        )
        try:
            orm_model = await repository.create_one(
                instance=instance
            )
        except CustomException as exc:
            return ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE(),
                    "detail": exc.msg,
                }
            )
        instance: RequestRead = RequestRead.model_validate(orm_model)
        await KafkaConfigurer.send_message(instance.model_dump(), topic_name=CLASS.lower())
        return instance
