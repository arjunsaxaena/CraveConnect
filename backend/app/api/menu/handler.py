from fastapi import APIRouter
from .menu_items import router as menu_items_router
from .addons import router as addons_router
from .menu_item_options import router as menu_item_options_router

router = APIRouter()

router.include_router(menu_items_router)
router.include_router(addons_router)
router.include_router(menu_item_options_router)