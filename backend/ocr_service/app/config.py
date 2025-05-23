import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://localhost:8002/api/menu")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

TEXT_MODEL = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config=generation_config
)

VISION_MODEL = genai.GenerativeModel(
    'gemini-1.5-flash',  
    generation_config=generation_config
)

EMBEDDING_MODEL = "models/embedding-001"