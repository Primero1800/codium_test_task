from fastapi import APIRouter

from src.core.settings import settings


router = APIRouter()

# router.include_router(
#     auth_router,
#     prefix=settings.tags.AUTH_PREFIX,
#     tags=[settings.tags.AUTH_TAG]
# )
#
#
# router.include_router(
#     users_router,
# )
