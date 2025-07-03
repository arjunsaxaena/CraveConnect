from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class MenuItemEmbeddingCreate(BaseModel):
    menu_item_id: UUID
    embedding: List[float]
    meta: Optional[dict] = {} 