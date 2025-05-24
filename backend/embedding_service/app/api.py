import requests
import json
from typing import Dict, Any, List, Optional
from app.config import logger, MENU_SERVICE_URL
import traceback
from pgvector import Vector

def update_menu_item_embedding(menu_item_id: str, embedding: List[float]) -> bool:
    """
    Update a menu item with its embedding vector.
    
    Args:
        menu_item_id: The ID of the menu item to update
        embedding: The embedding vector to store
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        endpoint = f"{MENU_SERVICE_URL}/api/menu/update-embedding"
        
        # Convert the embedding to a Vector format for pgvector
        payload = {
            "id": menu_item_id,
            "embedding": embedding
        }
        
        logger.info(f"Sending embedding update request for menu item {menu_item_id}")
        
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to update menu item embedding: {response.text}")
            return False
            
        logger.info(f"Successfully updated embedding for menu item {menu_item_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating menu item embedding: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def get_menu_item(menu_item_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a menu item by its ID.
    
    Args:
        menu_item_id: The ID of the menu item
        
    Returns:
        Dict containing menu item data or None if not found
    """
    try:
        endpoint = f"{MENU_SERVICE_URL}/api/menu/items?id={menu_item_id}"
        
        response = requests.get(endpoint)
        
        if response.status_code != 200:
            logger.error(f"Failed to get menu item: {response.text}")
            return None
            
        items = response.json()
        if not items or len(items) == 0:
            logger.error(f"Menu item not found: {menu_item_id}")
            return None
            
        return items[0]
        
    except Exception as e:
        logger.error(f"Error getting menu item: {str(e)}")
        logger.error(traceback.format_exc())
        return None 