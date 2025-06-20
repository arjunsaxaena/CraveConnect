from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class ReviewCreate(BaseModel):
    user_id: UUID
    restaurant_id: UUID
    rating: int
    comment: Optional[str] = None
    meta: Optional[dict] = None

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
    meta: Optional[dict] = None

class ReviewOut(BaseModel):
    id: UUID
    user_id: UUID
    restaurant_id: UUID
    rating: int
    comment: Optional[str] = None
    meta: Optional[dict] = None

    model_config = {
        "from_attributes": True
    }

class ReviewListResponse(BaseModel):
    data: List[ReviewOut]
    message: str = "Reviews fetched successfully"

class ReviewSingleResponse(BaseModel):
    data: ReviewOut
    message: str = "Review fetched successfully"
