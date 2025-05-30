import asyncio
from typing import List, Optional
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import logger, GEMINI_API_KEY, EMBEDDING_MODEL

# Initialize embedding model
genai.configure(api_key=GEMINI_API_KEY)
embedding_model = None

if GEMINI_API_KEY:
    try:
        embedding_model = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GEMINI_API_KEY,
            credentials=None
        )
    except Exception as e:
        logger.error(f"Error initializing embedding model: {str(e)}")

async def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for the given text."""
    if not embedding_model:
        logger.error("Embedding model not initialized")
        return None
        
    try:
        return await asyncio.to_thread(embedding_model.embed_query, text)
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return None