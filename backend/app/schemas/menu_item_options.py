from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

class MenuItemOptionCreate(BaseModel):
    menu_item_id: UUID
    name: str
    description: Optional[str] = None
    price: float
    meta: Optional[dict] = None

class MenuItemOptionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    meta: Optional[dict] = None

class MenuItemOptionOut(BaseModel):
    id: UUID
    menu_item_id: UUID
    name: str
    description: Optional[str] = None
    price: float
    meta: Optional[dict] = None

    model_config = {
        "from_attributes": True
    }

class MenuItemOptionListResponse(BaseModel):
    data: List[MenuItemOptionOut]
    message: str = "Menu item options fetched successfully"

class MenuItemOptionSingleResponse(BaseModel):
    data: MenuItemOptionOut
    message: str = "Menu item option fetched successfully"