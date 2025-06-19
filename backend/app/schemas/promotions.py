from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class PromotionCreate(BaseModel):
    restaurant_id: UUID
    title: str
    description: Optional[str] = None
    discount_percent: float
    valid_from: datetime
    valid_to: datetime
    meta: Optional[dict] = None

class PromotionUpdate(BaseModel):
    restaurant_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    discount_percent: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    meta: Optional[dict] = None

class PromotionOut(BaseModel):
    id: UUID
    restaurant_id: UUID
    title: str
    description: Optional[str] = None
    discount_percent: float
    valid_from: datetime
    valid_to: datetime
    meta: Optional[dict] = None

    model_config = {
        "from_attributes": True
    }

class PromotionListResponse(BaseModel):
    data: List[PromotionOut]
    message: str = "Promotions fetched successfully"

class PromotionSingleResponse(BaseModel):
    data: PromotionOut
    message: str = "Promotion fetched successfully"