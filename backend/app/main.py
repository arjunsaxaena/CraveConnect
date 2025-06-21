from fastapi import FastAPI
from app.api.user.handler import router as user_router
from app.api.restaurant.handler import router as restaurant_router
from app.api.menu.handler import router as menu_router
from app.api.orders.handler import router as orders_router

app = FastAPI()

ROUTERS = [
    user_router,
    restaurant_router,
    menu_router,
    orders_router,
]

for router in ROUTERS:
    app.include_router(router, prefix="/v1/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=4001, reload=True)

# uvicorn app.main:app --port 4001 --reload
