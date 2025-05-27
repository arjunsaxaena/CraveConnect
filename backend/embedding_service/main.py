from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.data_pipeline_service.app.routes import router

app = FastAPI(title="Data Pipeline Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
    
# uvicorn backend.data_pipeline_service.main:app --reload --port 8003 