from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    UPLOADS_DIR: str = "uploads"
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings() 