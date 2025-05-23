import logging

from fastapi import status
from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TYPE_CHECKING, Optional

from src.core.models import Request
from src.tools.exceptions import CustomException

from .exceptions import Errors

if TYPE_CHECKING:
    from src.api.v1.requests.filters import RequestFilter
    from .schemas import RequestCreate


logger = logging.Logger(__name__)


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logger

    async def get_all(
            self,
            filter_model: "RequestFilter",
            page: Optional[int] = 1,
            size: Optional[int] = 10,
    ):
        query_filter = filter_model.filter(select(Request))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.order_by(Request.id)

        stmt = stmt.offset((page - 1) * size).limit(size)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def create_one(
            self,
            instance: "RequestCreate"
    ):
        try:
            orm_model: Request = Request(**instance.model_dump())
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            return orm_model
        except IntegrityError as exc:
            self.logger.error("Error occurred while creating new item in database", exc_info=exc)
            raise CustomException(
                msg=Errors.DATABASE_ERROR(),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
