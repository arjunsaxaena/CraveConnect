from fastapi import APIRouter
from .restaurant import router as restaurant_router


router = APIRouter()


router.include_router(restaurant_router)