import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://localhost:8002")

# Model configuration
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/embedding-001")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("embedding-service")

# Validate required environment variables
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY not set. Embedding generation will fail.") 