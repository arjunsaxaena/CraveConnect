import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("data_pipeline_service")

MENU_SERVICE_URL = os.environ.get("MENU_SERVICE_URL", "http://localhost:8002")

OCR_ENABLED = os.environ.get("OCR_ENABLED", "true").lower() == "true"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemini-1.5-flash")
TEXT_MODEL = os.environ.get("TEXT_MODEL", "gemini-1.5-flash")

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "models/embedding-001")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "") 