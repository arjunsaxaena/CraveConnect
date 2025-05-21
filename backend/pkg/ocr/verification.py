"""
Verification Module for validating menu items and restaurant data.
"""
import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def verify_menu_items(menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verify menu items before API submission.
    """
    valid_items = []
    invalid_items = []
    warnings = []
    
    for item in menu_items:
        errors = []
        
        # Required fields validation
        if not item.get("name"):
            errors.append("Name is required")
        
        if not item.get("restaurant_id"):
            errors.append("Restaurant ID is required")
        
        # Price validation
        if item.get("price", 0) <= 0:
            errors.append(f"Price must be positive (got {item.get('price', 0)})")
        
        # Warning checks
        if item.get("price", 0) > 10000:
            warnings.append(f"Unusually high price: {item.get('name')} - ${item.get('price')}")
        
        # Add item to appropriate list
        if errors:
            invalid_items.append({"item": item, "errors": errors})
        else:
            valid_items.append(item)
    
    return {
        "valid": len(invalid_items) == 0,
        "items": valid_items,
        "invalid_items": invalid_items,
        "warnings": warnings
    }


def verify_restaurant_exists(
    restaurant_id: str, 
    api_base_url: str, 
    api_key: Optional[str] = None
) -> bool:
    """
    Verify that a restaurant exists before processing its menu items.
    """
    try:
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        endpoint = f"{api_base_url.rstrip('/')}/api/restaurants?id={restaurant_id}"
        response = requests.get(endpoint, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return len(result) > 0
        return False
    
    except Exception as e:
        logger.warning(f"Restaurant verification failed: {e}")
        return False
