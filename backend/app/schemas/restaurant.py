from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from app.schemas.user import Address

class RestaurantCreate(BaseModel):
    name: str
    address: Optional[Address] = None
    owner_id: UUID
    meta: Optional[dict] = None

class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[Address] = None
    owner_id: Optional[UUID] = None
    meta: Optional[dict] = None

class RestaurantOut(BaseModel):
    id: UUID
    name: str
    address: Optional[Address]
    owner_id: UUID
    meta: Optional[dict]

    model_config = {
        "from_attributes": True
    }

class RestaurantListResponse(BaseModel):
    data: List[RestaurantOut]
    message: str = "Restaurants fetched successfully"

class RestaurantSingleResponse(BaseModel):
    data: RestaurantOut
    message: str = "Restaurant fetched successfully"
