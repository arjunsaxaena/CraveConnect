from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.schemas import RecommendationRequest, RecommendationResponse
from app.recommendation_graph import process_recommendation
from app.config import logger, TOP_K

router = APIRouter()

@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_dishes(request: RecommendationRequest) -> Dict[str, Any]:
    """
    Recommend dishes based on user's craving description.
    
    Example:
        {"query": "I want something spicy and creamy", "top_k": 5}
    """
    logger.info(f"Recommendation request: {request.query}")
    
    try:
        top_k = request.top_k or TOP_K
        
        result = await process_recommendation(
            query=request.query,
            top_k=top_k
        )
        
        # Add debug info about what's in the database
        try:
            from app.vector_search import get_cuisine_distribution
            result["debug_info"] = {
                "cuisines_available": await get_cuisine_distribution(limit=10)
            }
        except Exception as e:
            logger.error(f"Error adding debug info: {str(e)}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing recommendation request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation processing failed: {str(e)}"
        )

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "recommendation_service"}