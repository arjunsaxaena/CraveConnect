from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class SessionLocation(BaseModel):
    latitude: float
    longitude: float

class UserCreate(BaseModel):
    name: str
    email: str
    provider: str
    session_location: Optional[SessionLocation] = None
    meta: Optional[dict] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    provider: Optional[str] = None
    session_location: Optional[SessionLocation] = None
    meta: Optional[dict] = None

class UserOut(BaseModel):
    id: UUID
    name: str
    email: str
    provider: str
    session_location: Optional[SessionLocation] = None
    meta: Optional[dict]

    model_config = {
        "from_attributes": True
    }

class UserListResponse(BaseModel):
    data: list[UserOut]
    message: str = "Users fetched successfully"

class UserSingleResponse(BaseModel):
    data: UserOut
    message: str = "User fetched successfully"
