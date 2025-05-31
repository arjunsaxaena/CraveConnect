"""Configuration settings for the embedding service.

This module centralizes all configuration and environment variable management.
"""

import os
import logging
from typing import Dict, Any
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("embedding_service")


class Settings(BaseSettings):
    """Settings for the embedding service."""

    # Service configuration
    menu_service_url: str = os.getenv("MENU_SERVICE_URL", "http://localhost:8002")
    service_port: int = int(os.getenv("SERVICE_PORT", "8003"))

    # API Keys and model configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "models/embedding-001")
    ocr_enabled: bool = os.getenv("OCR_ENABLED", "true").lower() == "true"

    # LLM generation settings
    generation_config: Dict[str, Any] = {
        "temperature": 0.2,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    class Config:
        """Pydantic config"""
        env_prefix = "APP_"
        case_sensitive = False


# Create settings instance
settings = Settings()

# For compatibility with existing code
MENU_SERVICE_URL = settings.menu_service_url
OCR_ENABLED = settings.ocr_enabled
GEMINI_API_KEY = settings.gemini_api_key
LLM_MODEL = settings.llm_model
EMBEDDING_MODEL = settings.embedding_model
GENERATION_CONFIG = settings.generation_config
