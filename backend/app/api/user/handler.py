from fastapi import APIRouter
from .user import router as user_router
from .favorites import router as favorites_router
from .user_preferences import router as user_preferences_router
from .reviews import router as reviews_router
from .address import router as address_router


router = APIRouter()


router.include_router(user_router)
router.include_router(favorites_router)
router.include_router(user_preferences_router)
router.include_router(reviews_router)
router.include_router(address_router)