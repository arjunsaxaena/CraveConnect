import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.embeddings.base import Embeddings
from typing import List, Dict, Any, Optional
from backend.data_pipeline_service.app.config import logger, GEMINI_API_KEY, EMBEDDING_MODEL

# Initialize Google Generative AI with API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the embedding model
embedding_model = None
try:
    if GEMINI_API_KEY:
        embedding_model = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GEMINI_API_KEY,
            credentials=None  # Explicitly disable ADC
        )
        logger.info(f"Embedding model initialized: {EMBEDDING_MODEL}")
    else:
        logger.warning("No Gemini API key provided. Embedding functionality will be disabled.")
except Exception as e:
    logger.error(f"Error initializing embedding model: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate embedding vector for a given text.
    
    Args:
        text: Text to generate embedding for
        
    Returns:
        List of floats representing the embedding vector or None if failed
    """
    try:
        if not embedding_model:
            logger.warning("Embedding model not initialized. Cannot generate embeddings.")
            return None
            
        if not text or text.strip() == "":
            logger.warning("Cannot generate embedding for empty text")
            return None
            
        # Generate embedding using LangChain
        try:
            embedding = embedding_model.embed_query(text)
            
            if not embedding or len(embedding) == 0:
                logger.warning("Embedding generation returned empty result")
                return None
                
            # Ensure we have the correct format for pgvector
            # pgvector expects a List[float] with proper float values
            embedding = [float(val) for val in embedding]
                
            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
        except Exception as e:
            logger.error(f"Error calling embedding model: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
        
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def generate_menu_item_embedding(menu_item: Dict[str, Any]) -> Optional[List[float]]:
    """
    Generate embedding for a menu item.
    
    Args:
        menu_item: Dictionary containing menu item data
        
    Returns:
        List of floats representing the embedding vector or None if failed
    """
    try:
        if not embedding_model:
            logger.warning("Embedding model not initialized. Cannot generate menu item embedding.")
            return None
            
        # Combine relevant fields for embedding
        name = menu_item.get("name", "")
        description = menu_item.get("description", "")
        size = menu_item.get("size", "")
        
        # Get category from meta if it exists
        category = ""
        if "meta" in menu_item and menu_item["meta"]:
            try:
                import json
                meta_data = json.loads(menu_item["meta"])
                category = meta_data.get("category", "")
            except:
                pass
            
        # Create combined text for embedding
        combined_text = f"{name}. {description}"
        if category:
            combined_text += f". Category: {category}"
        if size:
            combined_text += f". Size: {size}"
            
        logger.info(f"Generating embedding for: {combined_text}")
        
        # Generate the embedding
        embedding = generate_embedding(combined_text)
        
        if embedding:
            logger.info(f"Successfully generated embedding for menu item: {name}")
            return embedding
        else:
            logger.error(f"Failed to generate embedding for menu item: {name}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating menu item embedding: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None 