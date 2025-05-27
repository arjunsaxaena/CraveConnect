import requests
from typing import List, Dict, Any, Optional
from backend.data_pipeline_service.app.config import logger, MENU_SERVICE_URL
import traceback

def send_menu_items_with_embeddings(menu_items: List[Dict[str, Any]]) -> bool:
    """
    Send menu items with embeddings to the menu service.
    
    This function sends each menu item to the menu service API.
    
    Args:
        menu_items: List of menu items with embeddings
        
    Returns:
        bool: True if all items were sent successfully, False otherwise
    """
    try:
        url = MENU_SERVICE_URL
        if not url.endswith("/api/menu"):
            url = f"{url}/api/menu" if url.endswith("/") else f"{url}/api/menu"
        
        success_count = 0
        for i, item in enumerate(menu_items):
            try:
                # Check if embedding exists
                has_embedding = "embedding" in item and item["embedding"] is not None
                if not has_embedding:
                    logger.warning(f"Menu item '{item.get('name')}' has no embedding")
                
                # Format the item to match the menu service's expected structure
                formatted_item = {
                    "restaurant_id": item.get("restaurant_id", ""),
                    "name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "price": float(item.get("price", 0)),
                    "size": item.get("size", ""),
                    "image_path": item.get("image_path", ""),
                }
                
                # Add embedding if it exists
                if has_embedding:
                    formatted_item["embedding"] = item["embedding"]
                
                # Convert category and other attributes to meta if they exist
                meta = {}
                if "category" in item and item["category"]:
                    meta["category"] = item["category"]
                if "attributes" in item and item["attributes"]:
                    meta.update(item["attributes"])
                
                if meta:
                    import json
                    formatted_item["meta"] = json.dumps(meta)
                
                # Log the item being sent (without embedding for brevity)
                log_item = formatted_item.copy()
                if "embedding" in log_item:
                    log_item["embedding"] = f"[{len(log_item['embedding'])} dimensions]" if log_item["embedding"] else None
                logger.info(f"Sending menu item {i+1}/{len(menu_items)}: {log_item}")
                
                # Make the API request
                response = requests.post(url, json=formatted_item)
                
                if response.status_code != 201 and response.status_code != 200:
                    logger.error(f"Failed to create menu item '{item.get('name')}': HTTP {response.status_code}")
                    logger.error(f"Response: {response.text}")
                else:
                    success_count += 1
                    logger.info(f"Successfully created menu item: {item.get('name')}")
            except Exception as item_error:
                logger.error(f"Error sending menu item {i+1}: {str(item_error)}")
                continue
        
        if success_count == len(menu_items):
            logger.info(f"Successfully sent all {len(menu_items)} menu items to menu service")
            return True
        elif success_count > 0:
            logger.warning(f"Partially successful: sent {success_count} out of {len(menu_items)} menu items")
            return True
        else:
            logger.error(f"Failed to send any of the {len(menu_items)} menu items")
            return False
        
    except Exception as e:
        logger.error(f"Error sending menu items to API: {e}")
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