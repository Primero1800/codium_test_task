from fastapi import APIRouter, status, Request, Query, Depends
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.requests.schemas import RequestRead
from src.core.config import RateLimiter, DBConfigurer
from src.scripts.pagination import paginate_result

from .filters import RequestFilter
from .service import Service

router = APIRouter()


@router.get(
    "/",
    response_model=list[RequestRead],
    description="Get all items",
    status_code=status.HTTP_200_OK
)
@RateLimiter.rate_limit()
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: RequestFilter = FilterDepends(RequestFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: Service = Service(
        session=session
    )
    result_list: list = await service.get_all(filter_model=filter_model)
    return await paginate_result(
        query_list=result_list,
        page=page,
        size=size,
    )
