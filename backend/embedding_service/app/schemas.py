from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import json

class MenuItem(BaseModel):
    restaurant_id: str
    category_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    nutritional_info: Optional[Dict[str, Any]] = None
    prices: Dict[str, float]
    is_spicy: bool = False
    is_vegetarian: bool = False
    is_available: bool = True
    popularity_score: float = 0.0
    embedding: Optional[List[float]] = None
    meta: Optional[Dict[str, Any]] = None

class MenuCategory(BaseModel):
    restaurant_id: str
    name: str
    description: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class MenuItemResponse(BaseModel):
    name: str
    price: Any
    category: Optional[str] = None

class MenuImageProcessingResult(BaseModel):
    image_name: str
    success: bool
    message: str
    item_count: int = 0
    items: List[MenuItem] = []
    error: Optional[str] = None

class MenuProcessingRequest(BaseModel):
    restaurant_id: str
    menu_image_data: bytes

class MenuProcessingResponse(BaseModel):
    success: bool
    message: str
    item_count: int = 0
    items: List[MenuItem] = []
    error: Optional[str] = None

class MenuProcessingBatchResponse(BaseModel):
    success: bool
    message: str
    image_count: int
    processed_count: int
    results: List[MenuImageProcessingResult]
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
        if not value or not value.strip():
            raise ValueError("Menu item name cannot be empty")
        return value.strip()

def map_to_menu_items(restaurant_id: str, extracted_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    menu_items = []
    
    for item in extracted_items:
        if not item or not item.get("name") or not item.get("price"):
            continue
            
        try:
            meta = {}
            if item.get("category"):
                meta["category"] = item.get("category")
                
            menu_item = {
                "restaurant_id": restaurant_id,
                "name": str(item.get("name")).strip(),
                "description": str(item.get("description", "")),
                "price": float(item.get("price", 0)),
                "size": str(item.get("size", "")),
                "image_path": "",
                "is_active": True,
                "meta": json.dumps(meta) if meta else "{}"
            }
            
            menu_items.append(menu_item)
        except (ValueError, TypeError):
            continue
            
    return menu_items

def validate_menu_items(menu_items: List[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
    if not menu_items:
        return False, "No valid menu items found"
        
    for item in menu_items:
        try:
            MenuItem(**item)
        except Exception as e:
            return False, f"Invalid menu item: {str(e)}"
            
    return True, None