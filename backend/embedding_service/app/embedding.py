import requests
from app.config import logger, GOOGLE_API_KEY, GEMINI_MODEL, GEMINI_API_URL
import numpy as np
from typing import List, Dict, Any, Optional, Union

def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate an embedding vector for the given text using Google's Gemini API.
    
    Args:
        text: The text to generate an embedding for
        
    Returns:
        List of floats representing the embedding vector or None if failed
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for embedding generation")
        return None
    
    try:
        # Clean and prepare text
        text = text.strip()
        
        # Call Gemini embedding API
        url = f"{GEMINI_API_URL}/{GEMINI_MODEL}:embedContent?key={GOOGLE_API_KEY}"
        
        payload = {
            "model": GEMINI_MODEL,
            "content": {
                "parts": [
                    {
                        "text": text
                    }
                ]
            }
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Extract the embedding vector
        embedding_data = response.json()
        embedding = embedding_data["embedding"]["values"]
        
        logger.info(f"Successfully generated embedding for text: {text[:50]}...")
        return embedding
        
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return None

def generate_menu_item_embedding(menu_item: Dict[str, Any]) -> Optional[List[float]]:
    """
    Generate an embedding for a menu item by combining its name, description, and other fields.
    
    Args:
        menu_item: Dictionary containing menu item details
        
    Returns:
        List of floats representing the embedding vector or None if failed
    """
    try:
        # Combine relevant fields into a single text
        text_parts = []
        
        if "name" in menu_item and menu_item["name"]:
            text_parts.append(f"Name: {menu_item['name']}")
            
        if "description" in menu_item and menu_item["description"]:
            text_parts.append(f"Description: {menu_item['description']}")
            
        if "size" in menu_item and menu_item["size"]:
            text_parts.append(f"Size: {menu_item['size']}")
            
        combined_text = " ".join(text_parts)
        
        if not combined_text:
            logger.warning("No valid text found in menu item for embedding generation")
            return None
            
        return generate_embedding(combined_text)
        
    except Exception as e:
        logger.error(f"Error generating menu item embedding: {str(e)}")
        return None 