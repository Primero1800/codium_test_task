from fastapi import APIRouter

from .requests import router as requests_router
from src.core.settings import settings


router = APIRouter()

router.include_router(
    requests_router,
    prefix=settings.tags.REQUESTS_PREFIX,
    tags=[settings.tags.REQUESTS_TAG]
)
