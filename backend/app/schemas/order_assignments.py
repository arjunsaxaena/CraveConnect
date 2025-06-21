from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
class OrderAssignmentCreate(BaseModel):
    order_id: str
    delivery_person_id: str
    assigned_at: datetime
    meta: Optional[dict] = None

class OrderAssignmentUpdate(BaseModel):
    order_id: Optional[str] = None
    delivery_person_id: Optional[str] = None
    updated_at: Optional[datetime] = None

class OrderAssignmentOut(BaseModel):
    id: str
    order_id: str
    delivery_person_id: str
    assigned_at: datetime
    updated_at: datetime
    meta: Optional[dict] = None
    
    model_config = {
        "from_attributes": True
    }

class OrderAssignmentListResponse(BaseModel):
    data: List[OrderAssignmentOut]
    message: str = "Order assignments fetched successfully"

class OrderAssignmentSingleResponse(BaseModel):
    data: OrderAssignmentOut
    message: str = "Order assignment fetched successfully"