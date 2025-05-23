from typing import Optional, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import Repository

if TYPE_CHECKING:
    from .filters import RequestFilter


class Service:
    def __init__(self, session: AsyncSession):
        self.session = session

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
