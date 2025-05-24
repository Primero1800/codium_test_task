from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import Request


class RequestFilter(Filter):
    user_name: Optional[str] = Field(description="Filter items if user_name equals", default=None)
    user_name__like: Optional[str] = Field(description="Filter items if user_name likes", default=None)
    order_by: Optional[list[str]] = Field(description="Parameters to order by", default=['id',])

    class Constants(Filter.Constants):
        model = Request
