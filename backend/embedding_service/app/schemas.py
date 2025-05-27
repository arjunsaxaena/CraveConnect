from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
import json

class MenuItem(BaseModel):
    id: Optional[str] = None
    restaurant_id: str
    name: str
    description: Optional[str] = ""
    price: float
    size: Optional[str] = ""
    image_path: Optional[str] = ""
    is_active: bool = True
    embedding: Optional[List[float]] = None
    meta: Optional[str] = None

class MenuItemResponse(BaseModel):
    success: bool
    menu_item_id: Optional[str] = None
    error: Optional[str] = None

class MenuProcessingRequest(BaseModel):
    restaurant_id: str
    menu_image_data: bytes

class MenuProcessingResponse(BaseModel):
    success: bool
    message: str
    item_count: Optional[int] = None
    items: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class ExtractedMenuItem(BaseModel):
    name: str
    price: float
    description: Optional[str] = ""
    category: Optional[str] = None
    size: Optional[str] = ""
    
    @validator('price')
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value
    
    @validator('name')
    def validate_name(cls, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Menu item name cannot be empty")
        return value

def map_to_menu_items(restaurant_id: str, extracted_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert extracted menu items to the format expected by the menu service."""
    menu_items = []
    
    for item in extracted_items:
        if not item:
            continue
            
        try:
            # Validate required fields
            if not item.get("name") or not item.get("price"):
                continue
            
            # Create meta with category if it exists    
            meta = {}
            if item.get("category"):
                meta["category"] = item.get("category")
                
            meta_json = json.dumps(meta) if meta else None
                
            menu_item = {
                "restaurant_id": restaurant_id,
                "name": item.get("name"),
                "description": item.get("description", ""),
                "price": float(item.get("price", 0)),
                "size": item.get("size", ""),
                "image_path": "",
                "is_active": True,
                "meta": meta_json
            }
            
            menu_items.append(menu_item)
            
        except Exception as e:
            continue
            
    return menu_items

def validate_menu_items(menu_items: List[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
    """Validate a list of menu items."""
    if not menu_items or len(menu_items) == 0:
        return False, "No valid menu items found"
        
    for item in menu_items:
        try:
            MenuItem(**item)
        except Exception as e:
            return False, f"Invalid menu item: {str(e)}"
            
    return True, None 