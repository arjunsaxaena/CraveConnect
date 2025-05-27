from fastapi import APIRouter, UploadFile, File, Form
from typing import Dict, Any
from app.config import logger
from app.pipeline import MenuProcessingPipeline
from app.schemas import MenuProcessingResponse

router = APIRouter()
pipeline = MenuProcessingPipeline()

@router.post("/process-menu", response_model=MenuProcessingResponse)
async def process_menu(
    restaurant_id: str = Form(...),
    menu_image: UploadFile = File(...)
) -> Dict[str, Any]:
    """Process a menu image and extract menu items with embeddings."""
    try:
        image_data = await menu_image.read()
        success, message, items = pipeline.process(restaurant_id, image_data)
        
        if not success:
            return MenuProcessingResponse(
                success=False,
                message="Failed to process menu",
                error=message
            )
        
        return MenuProcessingResponse(
            success=True,
            message=message,
            item_count=len(items),
            items=items
        )
        
    except Exception as e:
        logger.error(f"Error processing menu: {str(e)}")
        return MenuProcessingResponse(
            success=False,
            message="Error processing menu",
            error=str(e)
        )

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "embedding_service"}