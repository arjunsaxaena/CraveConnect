"""API routes for the embedding service.

Dependencies (like pipeline) can be injected for easier testing and modularity.
"""

import asyncio
from typing import Dict, Any, List

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends

from app.schemas import (
    MenuProcessingResponse,
    MenuProcessingBatchResponse,
    MenuImageProcessingResult
)
from app.pipeline import MenuProcessingPipeline
from app.config import logger

router = APIRouter()

# Create singleton pipeline instance
pipeline = MenuProcessingPipeline()


async def validate_restaurant_id(restaurant_id: str = Form(...)) -> str:
    """Validate restaurant ID.

    Args:
        restaurant_id: ID of the restaurant

    Returns:
        Validated restaurant ID
    """
    if not restaurant_id.strip():
        raise HTTPException(status_code=400, detail="Restaurant ID cannot be empty")
    return restaurant_id


async def validate_menu_image(menu_image: UploadFile = File(...)) -> UploadFile:
    """Validate menu image upload.

    Args:
        menu_image: Uploaded menu image

    Returns:
        Validated menu image
    """
    if not menu_image.filename:
        raise HTTPException(status_code=400, detail="Menu image filename cannot be empty")

    content_type = menu_image.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"Invalid file type: {content_type}")

    return menu_image


@router.post("/process-menu", response_model=MenuProcessingResponse)
async def process_menu(
    restaurant_id: str = Depends(validate_restaurant_id),
    menu_image: UploadFile = Depends(validate_menu_image)
) -> Dict[str, Any]:
    """Process a single menu image and extract menu items with embeddings.

    Args:
        restaurant_id: ID of the restaurant
        menu_image: Uploaded menu image file

    Returns:
        Response with processing results
    """
    logger.info("Received request for restaurant_id: %s", restaurant_id)
    logger.info("Processing image: %s, size: %s bytes", menu_image.filename, menu_image.size)

    try:
        image_data = await menu_image.read()
        logger.info("Successfully read image data: %s bytes", len(image_data))

        success, message, items = await pipeline.process(restaurant_id, image_data)
        logger.info(
            "Pipeline processing complete. Success: %s, Message: %s, Items: %s",
            success, message, len(items)
        )

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
        logger.error("Error processing menu: %s", str(e))
        return MenuProcessingResponse(
            success=False,
            message="Error processing menu",
            error=str(e)
        )


@router.post("/process-menu-batch", response_model=MenuProcessingBatchResponse)
async def process_menu_batch(
    restaurant_id: str = Depends(validate_restaurant_id),
    menu_images: List[UploadFile] = File(...)
) -> Dict[str, Any]:
    """Process multiple menu images in parallel and extract menu items with embeddings.

    Args:
        restaurant_id: ID of the restaurant
        menu_images: List of uploaded menu image files

    Returns:
        Response with batch processing results
    """
    logger.info("Received batch request for restaurant_id: %s", restaurant_id)
    logger.info("Processing %s images in parallel", len(menu_images))

    if not menu_images:
        return MenuProcessingBatchResponse(
            success=False,
            message="No images provided",
            image_count=0,
            processed_count=0,
            error="No images provided"
        )

    async def process_single_image(image: UploadFile) -> MenuImageProcessingResult:
        """Process a single image from the batch.

        Args:
            image: Menu image file

        Returns:
            Processing result for the image
        """
        try:
            logger.info("Processing image: %s, size: %s bytes", image.filename, image.size)
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
            logger.error("Error processing image %s: %s", image.filename, str(e))
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
        logger.error("Error in batch processing: %s", str(e))
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
