from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


base_user_name = Field(examples=["John Doe", "Sarah Connor"])
base_description = Field(examples=["Need advice", "Congratulate me!"])


class BaseRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_name: str = base_user_name
    description: str = base_description


class RequestRead(BaseRequest):
    id: int
    created_at: datetime


class RequestCreate(BaseRequest):
    pass
