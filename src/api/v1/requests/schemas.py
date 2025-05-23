from datetime import datetime

from pydantic import BaseModel


class BaseRequest(BaseModel):
    user_name: str
    description: str


class RequestRead(BaseRequest):
    id: int
    created_at: datetime


class RequestCreate(BaseRequest):
    pass
