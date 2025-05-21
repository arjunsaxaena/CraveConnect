"""
Schema Module for mapping parsed menu items to database schema.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def map_to_menuitems(
    menu_items: List[Dict[str, Any]], 
    restaurant_id: str,
    image_base_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Map LLM-parsed items to database schema.
    """
    if not restaurant_id:
        raise ValueError("Restaurant ID is required")
    
    try:
        now = datetime.now()
        mapped_items = []
        
        for item in menu_items:
            # Generate a unique ID
            item_id = str(uuid.uuid4())
            
            # Format name with size if present
            name = item.get('name', '')
            size = item.get('size')
            if size:
                name = f"{name} ({size})"
            
            # Sanitize price value
            price_str = str(item.get('price', 0)).replace('$', '').replace('₹', '')
            try:
                price = float(price_str)
            except ValueError:
                price = 0.0
                logger.warning(f"Invalid price format for {name}: {price_str}")
            
            # Generate image path if applicable
            image_path = None
            if image_base_path:
                image_path = f"{image_base_path}/{item_id}.jpg"
            
            # Create mapped item
            mapped_item = {
                "id": item_id,
                "restaurant_id": restaurant_id,
                "name": name,
                "description": item.get('description', ''),
                "price": price,
                "image_path": image_path,
                "is_active": True,
                "created_at": now,
                "updated_at": now
            }
            
            mapped_items.append(mapped_item)
        
        logger.info(f"Mapped {len(mapped_items)} items to database schema")
        return mapped_items
    
    except Exception as e:
        logger.error(f"Schema mapping failed: {e}")
        raise
