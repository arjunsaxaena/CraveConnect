from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_NEON: str
    SECRET_KEY: str
    UPLOADS_DIR: str = "uploads"
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings() 