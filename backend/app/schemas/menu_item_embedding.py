from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID

class MenuItemEmbeddingBase(BaseModel):
    embedding: List[float]
    meta: Optional[Dict[str, Any]] = None

class MenuItemEmbeddingCreate(MenuItemEmbeddingBase):
    menu_item_id: UUID

class MenuItemEmbeddingUpdate(MenuItemEmbeddingBase):
    pass

class MenuItemEmbeddingOut(MenuItemEmbeddingBase):
    menu_item_id: UUID
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class MenuItemEmbeddingResponse(BaseModel):
    data: MenuItemEmbeddingOut
    message: str = "Menu item embedding operation successful"
