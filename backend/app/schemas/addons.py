from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID

class AddonOption(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class AddonsCreate(BaseModel):
    name: str
    options: List[AddonOption]
    meta: Optional[dict] = None

class AddonsUpdate(BaseModel):
    name: Optional[str] = None
    options: Optional[List[AddonOption]] = None
    meta: Optional[dict] = None

class AddonsOut(BaseModel):
    id: UUID
    name: str
    options: List[AddonOption]
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