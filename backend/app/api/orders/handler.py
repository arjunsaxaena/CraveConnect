from fastapi import APIRouter
from .orders import router as orders_router
from .delivery_persons import router as delivery_persons_router
from .order_assignments import router as order_assignments_router

router = APIRouter()

router.include_router(orders_router)
router.include_router(delivery_persons_router)
router.include_router(order_assignments_router)
