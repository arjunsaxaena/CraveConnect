from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from typing import Dict, Any
from app.schemas import MenuProcessingResponse
from app.pipeline import MenuProcessingPipeline
from app.config import logger

router = APIRouter()
pipeline = MenuProcessingPipeline()

@router.post("/process-menu", response_model=MenuProcessingResponse)
async def process_menu(
    restaurant_id: str = Form(...),
    menu_image: UploadFile = File(...)
) -> Dict[str, Any]:
    """Process a menu image and extract menu items with embeddings."""
    logger.info(f"Received request for restaurant_id: {restaurant_id}")
    logger.info(f"Processing image: {menu_image.filename}, size: {menu_image.size} bytes")
    
    try:
        image_data = await menu_image.read()
        logger.info(f"Successfully read image data: {len(image_data)} bytes")
        
        success, message, items = await pipeline.process(restaurant_id, image_data)
        logger.info(f"Pipeline processing complete. Success: {success}, Message: {message}, Items: {len(items)}")
        
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