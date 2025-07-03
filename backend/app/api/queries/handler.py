from fastapi import APIRouter
from app.api.queries.queries import router as queries_router

router = APIRouter()

router.include_router(queries_router) 