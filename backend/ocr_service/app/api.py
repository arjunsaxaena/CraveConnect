import requests
from typing import List, Dict
from app.config import logger, MENU_SERVICE_URL

def send_menu_items(menu_items: List[Dict]) -> bool:
    try:
        url = MENU_SERVICE_URL
        if not url.endswith("/api/menu"):
            url = f"{url}/api/menu" if url.endswith("/") else f"{url}/api/menu"
            
        for item in menu_items:
            response = requests.post(url, json=item)
            
            if response.status_code != 201 and response.status_code != 200:
                logger.error(f"Failed to create menu item '{item.get('name')}': {response.text}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Error sending menu items to API: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False