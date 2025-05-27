import requests
from typing import List, Dict, Any
from app.config import logger, MENU_SERVICE_URL

def send_menu_items_with_embeddings(menu_items: List[Dict[str, Any]]) -> bool:
    """Send menu items with embeddings to the menu service."""
    if not menu_items:
        return True
        
    url = f"{MENU_SERVICE_URL}/api/menu"
    success_count = 0
    
    for i, item in enumerate(menu_items):
        try:
            response = requests.post(url, json=item)
            
            if response.status_code in [200, 201]:
                success_count += 1
            else:
                logger.error(f"Failed to create menu item '{item.get('name')}': HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending menu item {i+1}: {str(e)}")
            continue
    
    success = success_count == len(menu_items)
    if not success:
        logger.warning(f"Only {success_count}/{len(menu_items)} menu items were successfully sent")
    
    return success