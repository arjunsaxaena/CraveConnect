from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from .menu_item_addons import MenuItemAddonsOut

class MenuItemOption(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class MenuItemCreate(BaseModel):
    restaurant_id: UUID
    name: str
    description: Optional[str] = None
    options: Optional[List[MenuItemOption]] = None
    tags: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    meta: Optional[dict] = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    options: Optional[List[MenuItemOption]] = None
    tags: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    meta: Optional[dict] = None

class MenuItemOut(BaseModel):
    id: UUID
    restaurant_id: UUID
    name: str
    description: Optional[str] = None
    options: Optional[List[MenuItemOption]] = None
    tags: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    meta: Optional[dict] = None
    addons: List[MenuItemAddonsOut] = []

    model_config = {
        "from_attributes": True
    }

class MenuItemListResponse(BaseModel):
    data: List[MenuItemOut]
    message: str = "Menu items fetched successfully"

class MenuItemSingleResponse(BaseModel):
    data: MenuItemOut
    message: str = "Menu item fetched successfully"