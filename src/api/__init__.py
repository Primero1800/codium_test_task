from fastapi import APIRouter

from .v1 import router as v1_router
from src.core.settings import settings

router = APIRouter()

router.include_router(
    v1_router,
    prefix=settings.app.API_V1_PREFIX
)
