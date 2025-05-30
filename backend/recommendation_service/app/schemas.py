from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RecommendationRequest(BaseModel):
    query: str
    top_k: int = 5

class DishRecommendation(BaseModel):
    id: str
    name: str
    description: str
    price: float
    restaurant_id: str
    restaurant_name: Optional[str] = None
    similarity_score: float
    category: Optional[str] = None

class RecommendationResponse(BaseModel):
    original_query: str
    refined_query: Optional[str] = None
    confidence: float
    recommendations: List[DishRecommendation]
    processing_info: Dict[str, Any] = {}