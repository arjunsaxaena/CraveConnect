from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    UPLOADS_DIR: str = "uploads"

    class Config:
        env_file = ".env" 