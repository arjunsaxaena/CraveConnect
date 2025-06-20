from pydantic import BaseModel
from typing import Optional, List

class OrderCreate(BaseModel):
    user_id: str
    restaurant_id: str
    total_price: float
    meta: Optional[dict] = None

class OrderUpdate(BaseModel):
    total_price: Optional[float] = None
    meta: Optional[dict] = None

class OrderOut(BaseModel):
    id: str
    user_id: str
    restaurant_id: str
    total_price: float
    meta: Optional[dict] = None

    model_config = {
        "from_attributes": True
    }

class OrderListResponse(BaseModel):
    data: List[OrderOut]
    message: str = "Orders fetched successfully"

class OrderSingleResponse(BaseModel):
    data: OrderOut
    message: str = "Order fetched successfully"