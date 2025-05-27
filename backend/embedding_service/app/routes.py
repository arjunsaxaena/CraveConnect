from fastapi import APIRouter, UploadFile, File, Form, Response, status, BackgroundTasks
from typing import Dict, Any
from backend.data_pipeline_service.app.config import logger
from backend.data_pipeline_service.app.pipeline import MenuProcessingPipeline
from backend.data_pipeline_service.app.schemas import MenuProcessingResponse

router = APIRouter()
pipeline = MenuProcessingPipeline()

@router.post("/process-menu", response_model=MenuProcessingResponse)
async def process_menu(
    restaurant_id: str = Form(...),
    menu_image: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Process a menu image to extract menu items, generate embeddings, and save to the menu service.
    
    This endpoint:
    1. Extracts text from the menu image using OCR
    2. Parses menu items from the text using LLMs
    3. Also parses menu items directly from the image using vision LLMs
    4. Merges results from both approaches
    5. Generates embeddings for each menu item
    6. Sends menu items with embeddings to the menu service
    
    Args:
        restaurant_id: ID of the restaurant
        menu_image: Image file of the menu
        
    Returns:
        JSON response with results of processing
    """
    try:
        # Read the image data
        image_data = await menu_image.read()
        
        # Process the menu image through the pipeline
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
        import traceback
        logger.error(traceback.format_exc())
        return MenuProcessingResponse(
            success=False,
            message="Error processing menu",
            error=str(e)
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status of the service
    """
    return {"status": "healthy", "service": "data-pipeline-service"} 