from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
class UserCreate(BaseModel):
    name: str
    email: str
    provider: str
    address: Optional[dict] = None
    meta: Optional[dict] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    provider: Optional[str] = None
    address: Optional[dict] = None
    meta: Optional[dict] = None

class UserOut(BaseModel):
    id: UUID
    name: str
    email: str
    provider: str
    address: Optional[dict]
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
