from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class AddressCreate(BaseModel):
    user_id: Optional[UUID] = None
    restaurant_id: Optional[UUID] = None
    alias: Optional[str] = None
    street: Optional[str] = None
    locality: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[int] = None
    landmark: Optional[str] = None
    is_primary: Optional[bool] = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    meta: Optional[dict] = None

class AddressUpdate(BaseModel):
    alias: Optional[str] = None
    street: Optional[str] = None
    locality: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[int] = None
    landmark: Optional[str] = None
    is_primary: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    meta: Optional[dict] = None

class AddressOut(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    restaurant_id: Optional[UUID] = None
    alias: Optional[str] = None
    street: Optional[str] = None
    locality: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[int] = None
    landmark: Optional[str] = None
    is_primary: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AddressListResponse(BaseModel):
    data: List[AddressOut]
    message: str = "Addresses fetched successfully"

class AddressSingleResponse(BaseModel):
    data: AddressOut
    message: str = "Address fetched successfully"