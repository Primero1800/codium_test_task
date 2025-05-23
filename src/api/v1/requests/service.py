import logging
from typing import Optional, TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from .repository import Repository
from .schemas import RequestCreate
from .exceptions import Errors

if TYPE_CHECKING:
    from .filters import RequestFilter


logger = logging.Logger(__name__)


class Service:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logger

    async def get_all(
            self,
            filter_model: Optional["RequestFilter"] = None
    ):
        repository: Repository = Repository(
            session=self.session
        )
        return await repository.get_all(
            filter_model=filter_model
        )

    async def create_one(
            self,
            instance: RequestCreate
    ):
        repository: Repository = Repository(
            session=self.session
        )
        try:
            return await repository.create_one(
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
