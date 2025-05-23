from typing import TYPE_CHECKING

from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import Request

if TYPE_CHECKING:
    from src.api.v1.requests.filters import RequestFilter


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
            self,
            filter_model: "RequestFilter"
    ):
        query_filter = filter_model.filter(select(Request))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.order_by(Request.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()
