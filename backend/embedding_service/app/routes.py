from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from typing import Dict, Any, List
from app.schemas import MenuProcessingResponse, MenuProcessingBatchResponse, MenuImageProcessingResult
from app.pipeline import MenuProcessingPipeline
from app.config import logger
import asyncio

router = APIRouter()
pipeline = MenuProcessingPipeline()

@router.post("/process-menu", response_model=MenuProcessingResponse)
async def process_menu(
    restaurant_id: str = Form(...),
    menu_image: UploadFile = File(...)
) -> Dict[str, Any]:
    """Process a single menu image and extract menu items with embeddings."""
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

@router.post("/process-menu-batch", response_model=MenuProcessingBatchResponse)
async def process_menu_batch(
    restaurant_id: str = Form(...),
    menu_images: List[UploadFile] = File(...)
) -> Dict[str, Any]:
    """Process multiple menu images in parallel and extract menu items with embeddings."""
    logger.info(f"Received batch request for restaurant_id: {restaurant_id}")
    logger.info(f"Processing {len(menu_images)} images in parallel")
    
    async def process_single_image(image):
        try:
            logger.info(f"Processing image: {image.filename}, size: {image.size} bytes")
            image_data = await image.read()
            success, message, items = await pipeline.process(restaurant_id, image_data)
            
            return MenuImageProcessingResult(
                image_name=image.filename,
                success=success,
                message=message,
                item_count=len(items),
                items=items[:10],  # Preview first 10 items
                error=None if success else message
            )
        except Exception as e:
            logger.error(f"Error processing image {image.filename}: {str(e)}")
            return MenuImageProcessingResult(
                image_name=image.filename,
                success=False,
                message="Error processing image",
                error=str(e)
            )
    
    try:
        # Process all images in parallel
        tasks = [process_single_image(image) for image in menu_images]
        results = await asyncio.gather(*tasks)
        
        # Count successful results
        processed_count = sum(1 for result in results if result.success)
        overall_success = processed_count > 0
        
        return MenuProcessingBatchResponse(
            success=overall_success,
            message=f"Processed {processed_count}/{len(menu_images)} images successfully",
            image_count=len(menu_images),
            processed_count=processed_count,
            results=results,
            error=None if overall_success else "Failed to process any images"
        )
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        return MenuProcessingBatchResponse(
            success=False,
            message="Error processing batch",
            image_count=len(menu_images),
            processed_count=0,
            error=str(e)
        )

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "embedding_service"}