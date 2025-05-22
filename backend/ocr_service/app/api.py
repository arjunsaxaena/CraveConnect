import requests
from typing import List, Dict
from app.config import logger, MENU_SERVICE_URL

def send_menu_items(menu_items: List[Dict]) -> bool:
    """Send menu items to the menu service API."""
    try:
        # Ensure URL has the correct endpoint
        url = MENU_SERVICE_URL
        if not url.endswith("/api/menu"):
            url = f"{url}/api/menu" if url.endswith("/") else f"{url}/api/menu"
            
        logger.info(f"Sending menu items to {url}")
        
        for item in menu_items:
            logger.info(f"Sending item: {item['name']}")
            response = requests.post(url, json=item)
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code != 201 and response.status_code != 200:
                logger.error(f"Failed to create menu item '{item.get('name')}': {response.text}")
                return False
        
        logger.info(f"Successfully created {len(menu_items)} menu items")
        return True
    except Exception as e:
        logger.error(f"Error sending menu items to API: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False