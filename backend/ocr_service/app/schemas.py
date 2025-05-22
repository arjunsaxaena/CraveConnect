from typing import List, Dict, Tuple, Optional
from app.config import logger

def map_to_menu_items(restaurant_id: str, items: List[Dict]) -> List[Dict]:
    """Map parsed items to the menu item schema."""
    menu_items = []
    
    for item in items:
        # Construct name with size if available
        name = item.get("name", "")
        if item.get("size"):
            name = f"{name} ({item.get('size')})"
        
        # Build description with category if available
        description = item.get("description") or ""
        if item.get("category") and "category" not in description.lower():
            description = f"Category: {item.get('category')}\n{description}".strip()
            
        menu_item = {
            "restaurant_id": restaurant_id,
            "name": name,
            "description": description,
            "price": float(item.get("price", 0)),
            "is_active": True
        }
        menu_items.append(menu_item)
        
    return menu_items

def validate_menu_items(menu_items: List[Dict]) -> Tuple[bool, Optional[str]]:
    """Verify menu items before sending to API."""
    if not menu_items:
        return False, "No menu items to process"
    
    for i, item in enumerate(menu_items):
        if not item.get("name"):
            return False, f"Item at position {i} has no name"
        
        if not item.get("restaurant_id"):
            return False, f"Item '{item.get('name')}' has no restaurant_id"
        
        try:
            price = float(item.get("price", 0))
            if price < 0:
                return False, f"Item '{item.get('name')}' has invalid price: {price}"
        except (ValueError, TypeError):
            return False, f"Item '{item.get('name')}' has non-numeric price: {item.get('price')}"

    return True, None