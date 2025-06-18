from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class FavoritesCreate(BaseModel):
    user_id: UUID
    menu_item_id: UUID
    meta: Optional[dict] = None

class FavoritesUpdate(BaseModel):
    meta: Optional[dict] = None

class FavoritesOut(BaseModel):
    user_id: UUID
    menu_item_id: UUID
    created_at: Optional[str]
    updated_at: Optional[str]
    meta: Optional[dict]

    model_config = {
        "from_attributes": True
    }

class FavoritesListResponse(BaseModel):
    data: List[FavoritesOut]
    message: str = "Favorites fetched successfully"

class FavoritesSingleResponse(BaseModel):
    data: FavoritesOut
    message: str = "Favorite fetched successfully" 