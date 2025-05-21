"""
API Module for communicating with the backend services.
"""
import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def submit_menu_items_api(
    menu_items: List[Dict[str, Any]],
    api_base_url: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    if not api_base_url:
        raise ValueError("API base URL is required")
    
    try:
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        endpoint = f"{api_base_url.rstrip('/')}/api/menu/bulk"
        response = requests.post(
            endpoint,
            headers=headers,
            json={"items": menu_items},
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"API submission successful: {len(menu_items)} items")
        return result
    
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response:
            error_msg = f"{error_msg}: {e.response.text}"
            
        logger.error(f"API submission failed: {error_msg}")
        raise
