from pydantic import BaseModel
from typing import List
from uuid import UUID

class MenuItemAddonsCreate(BaseModel):
    menu_item_id: UUID
    addon_id: UUID

class MenuItemAddonsOut(BaseModel):
    menu_item_id: UUID
    addon_id: UUID

    model_config = {
        "from_attributes": True
    }

class MenuItemAddonsListResponse(BaseModel):
    data: List[MenuItemAddonsOut]
    message: str = "Menu item addons fetched successfully"

class MenuItemAddonsSingleResponse(BaseModel):
    data: MenuItemAddonsOut
    message: str = "Menu item addon fetched successfully" 