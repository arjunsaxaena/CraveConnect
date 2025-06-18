from fastapi import FastAPI
from app.api.user.handler import router as user_router

app = FastAPI()

app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=4001, reload=True)

# uvicorn app.main:app --port 4001 --reload
