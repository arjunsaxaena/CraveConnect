import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import asyncio
from typing import List, Dict, Any, Optional
from app.config import logger, GEMINI_API_KEY, EMBEDDING_MODEL

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
    if not embedding_model:
        return None
        
    try:
        return await asyncio.to_thread(embedding_model.embed_query, text)
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return None

async def generate_menu_item_embedding(item: Dict[str, Any]) -> List[float]:
    try:
        item_text = item.get("name", "")
        
        if "size" in item and item["size"]:
            item_text += f" {item['size']}"
            
        if "description" in item and item["description"]:
            item_text += f". {item['description']}"
            
        if "category" in item and item["category"]:
            item_text += f". Category: {item['category']}"
            
        return await generate_embedding(item_text)
        
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return []