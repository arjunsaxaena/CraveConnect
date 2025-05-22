import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API endpoints from environment
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://localhost:8002/api/menu")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google AI
genai.configure(api_key=GEMINI_API_KEY)

# Update models to use currently available ones with better rate limits
TEXT_MODEL = genai.GenerativeModel('gemini-1.5-flash')  # Changed from gemini-1.5-pro for better rate limits
VISION_MODEL = genai.GenerativeModel('gemini-1.5-flash')  # Changed from deprecated gemini-pro-vision

# Optional model for embedding if needed
EMBEDDING_MODEL = "models/embedding-001"