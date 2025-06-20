from fastapi import APIRouter
from .menu_items import router as menu_items_router

router = APIRouter()

router.include_router(menu_items_router)
