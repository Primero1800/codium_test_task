from fastapi import APIRouter, status, Request, Query, Depends
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.requests.schemas import RequestRead, RequestCreate
from src.core.config import RateLimiter, DBConfigurer

from .filters import RequestFilter
from .service import Service

router = APIRouter()


@router.get(
        "/",
        response_model=list[RequestRead],
        status_code=status.HTTP_200_OK,
        description="Get all items",
        responses={
            200: {
                "content": {
                    "application/json": {
                        "examples": {
                            "example1": {
                                "summary": "A list of requests",
                                "value": [
                                    {
                                        "id": 1,
                                        "user_name": "John Doe",
                                        "description": "Congratulate me!",
                                        "created_at": "2025-05-23 13:56:40.122397"
                                    },
                                    {
                                        "id": 2,
                                        "user_name": "Sarah Connor",
                                        "description": "Need advice",
                                        "created_at": "2025-05-23 13:58:40.122397"
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            422: {
                "description": "Validation Error",
                "content": {
                    "application/json": {
                        "examples": {
                            "invalid input": {
                                "summary": "Invalid input data",
                                "value": {
                                    "detail": [
                                        {
                                            "loc": ["query", "page"],
                                            "msg": "Input should be greater than 0",
                                            "type": "greater_than"
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            500: {
                "description": "Internal Server Error",
                "content": {
                    "application/json": {
                        "examples": {
                            "internal_error": {
                                "summary": "Database insertion error",
                                "value": {
                                    "message": "Internal server error",
                                    "detail": "IntegrityError: duplicate key value violates unique constraint"
                                }
                            }
                        }
                    }
                }
            },
        }
)
@RateLimiter.rate_limit()
async def get_all(
        request: Request,
        page: int = Query(1, gt=0, description="Result list page number, greater than 0"),
        size: int = Query(10, gt=0, description="Result list page size, greater than 0"),
        filter_model: RequestFilter = FilterDepends(RequestFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: Service = Service(
        session=session
    )
    return await service.get_all(
        filter_model=filter_model,
        page=page,
        size=size
    )


@router.post(
    "/",
    response_model=RequestRead,
    status_code=status.HTTP_200_OK,
    description="Create one item",
    responses={
        200: {
            "content": {
                "application/json": {
                    "examples": {
                        "example1": {
                            "summary": "A new request",
                            "value": {
                                "id": 1,
                                "user_name": "John Doe",
                                "description": "Congratulate me!",
                                "created_at": "2025-05-23 13:56:40.122397"
                            },
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid input": {
                            "summary": "Invalid input data",
                            "value": {
                                "detail": [
                                    {
                                        "loc": ["body", "user_name"],
                                        "msg": "Field required",
                                        "type": "missing"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "examples": {
                        "internal_error": {
                            "summary": "Database insertion error",
                            "value": {
                                "message": "Internal server error",
                                "detail": "IntegrityError: duplicate key value violates unique constraint"
                            }
                        }
                    }
                }
            }
        },
    }
)
@RateLimiter.rate_limit()
async def create_one(
        request: Request,
        instance: RequestCreate,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: Service = Service(
        session=session
    )
    return await service.create_one(
        instance=instance
    )
