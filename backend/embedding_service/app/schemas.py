"""Data schemas for the embedding service.

Defines all Pydantic models for menu items and related data. These models should be used throughout
the codebase for type safety, validation, and serialization.
"""

import json
from typing import List, Dict, Any, Optional, Tuple, Union
from pydantic import BaseModel, Field, field_validator, model_validator

class ExtractedMenuItem(BaseModel):
    """Schema for an extracted menu item."""

    name: str
    price: float = Field(gt=0, description="Price must be greater than 0")
    description: Optional[str] = ""
    category: Optional[str] = None
    size: Optional[str] = ""

    @field_validator('price')
    @classmethod
    def validate_price(cls, value: float) -> float:
        """Validate that price is greater than 0."""
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate that name is not empty."""
        if not value or not value.strip():
            raise ValueError("Menu item name cannot be empty")
        return value.strip()


class MenuItem(BaseModel):
    """Schema for a menu item with embedding."""

    restaurant_id: str
    name: str
    description: str = ""
    price: float = Field(gt=0, description="Price must be greater than 0")
    size: str = ""
    image_path: str = ""
    meta: str = "{}"
    is_active: bool = True
    embedding: Optional[List[float]] = None

    @model_validator(mode='before')
    @classmethod
    def ensure_meta_is_json_string(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure meta field is a JSON string."""
        if isinstance(data.get('meta'), dict):
            data['meta'] = json.dumps(data['meta'])
        return data


class MenuItemResponse(BaseModel):
    """Schema for menu item response."""

    name: str
    price: Union[float, str]
    category: Optional[str] = None


class MenuImageProcessingResult(BaseModel):
    """Schema for menu image processing result."""

    image_name: str
    success: bool
    message: str
    item_count: int = 0
    items: List[Dict[str, Any]] = []
    error: Optional[str] = None


class MenuProcessingRequest(BaseModel):
    """Schema for menu processing request."""

    restaurant_id: str
    menu_image_data: bytes


class MenuProcessingResponse(BaseModel):
    """Schema for menu processing response."""

    success: bool
    message: str
    item_count: int = 0
    items: List[Dict[str, Any]] = []
    error: Optional[str] = None


class MenuProcessingBatchResponse(BaseModel):
    """Schema for batch menu processing response."""

    success: bool
    message: str
    image_count: int
    processed_count: int
    results: List[MenuImageProcessingResult] = []
    error: Optional[str] = None


def map_to_menu_items(
    restaurant_id: str, extracted_items: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Convert extracted menu items to the format expected by the menu service."""
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


def validate_menu_items(menu_items: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    """Validate a list of menu items."""
    if not menu_items:
        return False, "No valid menu items found"

    for item in menu_items:
        try:
            MenuItem(**item)
        except Exception as e:
            return False, f"Invalid menu item: {str(e)}"

    return True, None
