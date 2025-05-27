import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("data_pipeline_service")

MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://localhost:8002")
OCR_ENABLED = os.getenv("OCR_ENABLED", "true").lower() == "true"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")

GENERATION_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}