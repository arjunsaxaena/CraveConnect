from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID

class RecommendationCreate(BaseModel):
    query_id: UUID
    menu_item_id: UUID
    confidence_score: float
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict) 