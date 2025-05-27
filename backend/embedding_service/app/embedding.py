import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from typing import List, Dict, Any, Optional
from app.config import logger, GEMINI_API_KEY, EMBEDDING_MODEL

# Initialize Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)

# Initialize embedding model
embedding_model = None
if GEMINI_API_KEY:
    try:
        embedding_model = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GEMINI_API_KEY,
            credentials=None
        )
        logger.info(f"Embedding model initialized: {EMBEDDING_MODEL}")
    except Exception as e:
        logger.error(f"Error initializing embedding model: {str(e)}")
        embedding_model = None
else:
    logger.warning("No Gemini API key provided. Embedding functionality disabled.")

def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for given text."""
    if not embedding_model or not text.strip():
        return None
        
    try:
        embeddings = embedding_model.embed_documents([text])
        return embeddings[0] if embeddings else None
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return None

def generate_menu_item_embedding(menu_item: Dict[str, Any]) -> Optional[List[float]]:
    """Generate embedding for a menu item by combining its text fields."""
    try:
        name = menu_item.get("name", "").strip()
        description = menu_item.get("description", "").strip()
        size = menu_item.get("size", "").strip()
        
        if not name:
            return None
            
        # Combine text fields for embedding
        text_parts = [name]
        if description:
            text_parts.append(description)
        if size:
            text_parts.append(f"Size: {size}")
            
        combined_text = ". ".join(text_parts)
        
        embedding = generate_embedding(combined_text)
        
        return embedding
        
    except Exception as e:
        logger.error(f"Error generating menu item embedding: {str(e)}")
        return None