from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class Address(BaseModel):
    alias: Optional[str] = None
    street: Optional[str] = None
    locality: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[int] = None
    landmark: Optional[str] = None
    latitude: float
    longitude: float

class UserCreate(BaseModel):
    name: str
    email: str
    provider: str
    address: Optional[List[Address]] = None
    meta: Optional[dict] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    provider: Optional[str] = None
    address: Optional[List[Address]] = None
    meta: Optional[dict] = None

class UserOut(BaseModel):
    id: UUID
    name: str
    email: str
    provider: str
    address: Optional[List[Address]]
    meta: Optional[dict]

    model_config = {
        "from_attributes": True
    }

class UserListResponse(BaseModel):
    data: List[UserOut]
    message: str = "Users fetched successfully"

class UserSingleResponse(BaseModel):
    data: UserOut
    message: str = "User fetched successfully"
