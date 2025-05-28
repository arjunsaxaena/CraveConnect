import aiohttp
import asyncio
from typing import List, Dict, Any
from app.config import MENU_SERVICE_URL, logger

async def send_menu_items_with_embeddings(menu_items: List[Dict[str, Any]]) -> bool:
    """Send menu items with embeddings to the menu service."""
    if not menu_items:
        logger.warning("No menu items to send")
        return True
        
    url = f"{MENU_SERVICE_URL}/api/menu" 
    success_count = 0
    
    try:
        logger.info(f"Sending {len(menu_items)} menu items to database at {url}")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in menu_items:
                tasks.append(session.post(url, json=item))
                
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"Error sending menu item {i+1}: {str(response)}")
                    continue
                    
                if response.status in [200, 201]:
                    success_count += 1
                else:
                    try:
                        error_text = await response.text()
                        logger.error(f"Failed to send item {i+1}: HTTP {response.status}, {error_text}")
                    except:
                        logger.error(f"Failed to send item {i+1}: HTTP {response.status}")
        
        success_rate = success_count / len(menu_items) if menu_items else 1.0
        logger.info(f"Sent {success_count}/{len(menu_items)} menu items ({success_rate:.0%})")
        
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Error sending menu items to database: {str(e)}")
        return False