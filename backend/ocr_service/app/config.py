import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ocr_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API endpoints from environment
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://localhost:8002/api/menu")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google AI
genai.configure(api_key=GEMINI_API_KEY)

# Set up generation config for better results with menus
generation_config = {
    "temperature": 0.2,  # Lower temperature for more consistent results
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,  # Allow for longer responses
}

# Update models
TEXT_MODEL = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config=generation_config
)

VISION_MODEL = genai.GenerativeModel(
    'gemini-1.5-flash',  
    generation_config=generation_config
)

# Optional model for embedding if needed
EMBEDDING_MODEL = "models/embedding-001"