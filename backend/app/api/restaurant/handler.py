from fastapi import APIRouter
from .restaurant import router as restaurant_router
from .promotions import router as promotion_router


router = APIRouter()


router.include_router(restaurant_router)
router.include_router(promotion_router)