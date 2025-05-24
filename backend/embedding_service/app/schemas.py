from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Dict, Any, Union
import json

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    size: Optional[str] = None
    restaurant_id: str
    
    class Config:
        extra = "allow"

class MenuItemRequest(MenuItemBase):
    id: Optional[str] = None
    
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('price must be non-negative')
        return v
    
    @validator('restaurant_id')
    def validate_restaurant_id(cls, v):
        if not v or not v.strip():
            raise ValueError('restaurant_id is required')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('name is required')
        return v

class EmbeddingResponse(BaseModel):
    success: bool
    embedding: Optional[List[float]] = None  # Truncated embedding for display
    full_embedding: Optional[List[float]] = None  # Full embedding for storage
    menu_item_id: Optional[str] = None
    error: Optional[str] = None

class MenuItemEmbeddingRequest(BaseModel):
    menu_item: MenuItemRequest
    
    class Config:
        schema_extra = {
            "example": {
                "menu_item": {
                    "id": "12345",
                    "name": "Margherita Pizza",
                    "description": "Classic pizza with tomato sauce, mozzarella, and basil",
                    "price": 12.99,
                    "size": "Medium",
                    "restaurant_id": "restaurant123"
                }
            }
        }

class BatchEmbeddingRequest(BaseModel):
    menu_items: List[MenuItemRequest]
    
    @validator('menu_items')
    def validate_menu_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('at least one menu item is required')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "menu_items": [
                    {
                        "id": "12345",
                        "name": "Margherita Pizza",
                        "description": "Classic pizza with tomato sauce, mozzarella, and basil",
                        "price": 12.99,
                        "size": "Medium",
                        "restaurant_id": "restaurant123"
                    },
                    {
                        "id": "67890",
                        "name": "Pepperoni Pizza",
                        "description": "Pizza with tomato sauce, mozzarella, and pepperoni",
                        "price": 14.99,
                        "size": "Large",
                        "restaurant_id": "restaurant123"
                    }
                ]
            }
        }

class BatchEmbeddingResponse(BaseModel):
    results: List[Dict[str, Any]]
    success_count: int
    failure_count: int 