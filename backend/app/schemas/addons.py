from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

class AddonsCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    meta: Optional[dict] = None

class AddonsUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    meta: Optional[dict] = None

class AddonsOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: float
    meta: Optional[dict] = None

    model_config = {
        "from_attributes": True
    }

class AddonsListResponse(BaseModel):
    data: List[AddonsOut]
    message: str = "Addons fetched successfully"

class AddonsSingleResponse(BaseModel):
    data: AddonsOut
    message: str = "Addon fetched successfully"