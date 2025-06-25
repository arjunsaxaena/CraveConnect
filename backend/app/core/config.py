from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()
print(f"DATABASE_URL from env: {os.getenv('DATABASE_URL')}")
print(f"GEMINI_API_KEY from env: {os.getenv('GEMINI_API_KEY')}")
print(f"UPLOADS_DIR from env: {os.getenv('UPLOADS_DIR', 'uploads')}")
print(f"COHERE_API_KEY from env: {os.getenv('COHERE_API_KEY')}")
class Settings(BaseSettings):
    DATABASE_URL: str
    UPLOADS_DIR: str = "uploads"
    GEMINI_API_KEY: str
    COHERE_API_KEY: str


settings = Settings() 