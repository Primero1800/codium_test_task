from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import Request


class RequestFilter(Filter):
    user_name: Optional[str] = Field(default=None, description="Filter by user_name", ),
    user_name__like: Optional[str] = Field(default=None, description="Filter by user_name contains", ),
    order_by: Optional[list[str]] = ['id']

    class Constants(Filter.Constants):
        model = Request
