from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class DeliveryPersonCreate(BaseModel):
    user_id: UUID
    name: str
    phone_number: str
    vehicle_details: str
    vehicle_type: str
    meta: Optional[dict] = None

class DeliveryPersonUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    vehicle_details: Optional[str] = None
    vehicle_type: Optional[str] = None
    meta: Optional[dict] = None

class DeliveryPersonOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    phone_number: str
    vehicle_details: str
    vehicle_type: str
    meta: Optional[dict] = None

    model_config = {
        "from_attributes": True
    }

class DeliveryPersonListResponse(BaseModel):
    data: List[DeliveryPersonOut]
    message: str = "Delivery persons fetched successfully"

class DeliveryPersonSingleResponse(BaseModel):
    data: DeliveryPersonOut
    message: str = "Delivery person fetched successfully"
