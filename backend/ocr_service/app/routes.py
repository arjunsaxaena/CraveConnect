from fastapi import APIRouter, UploadFile, File, Form, Response, status
from typing import Dict, Any
from app.config import logger
from app.ocr import extract_text
from app.llm import parse_menu_text, parse_menu_image
from app.schemas import map_to_menu_items, validate_menu_items, merge_menu_items
from app.api import send_menu_items

router = APIRouter()

@router.post("/process-menu")
async def process_menu(
    restaurant_id: str = Form(...),
    menu_image: UploadFile = File(...)
) -> Dict[str, Any]:
    """Process menu image with improved hybrid approach."""
    logger.info(f"Processing menu for restaurant_id: {restaurant_id}")
    
    try:
        # Step 1: Read image data
        image_data = await menu_image.read()
        logger.info(f"Read image data: {len(image_data)} bytes, content_type: {menu_image.content_type}")
        
        # Save image for debugging
        with open("debug_image.jpg", "wb") as f:
            f.write(image_data)
        logger.info("Saved debug image to disk")
        
        # Step 2: Run both approaches in parallel for redundancy
        # 2a. OCR + Text LLM approach
        menu_text = extract_text(image_data)
        ocr_items = []
        if menu_text and menu_text.strip():
            logger.info("Sending OCR text to LLM for parsing")
            ocr_items = parse_menu_text(menu_text)
            logger.info(f"Text LLM returned {len(ocr_items)} items from OCR text")
        else:
            logger.warning("OCR text extraction failed or returned empty result")
        
        # 2b. Vision API direct approach (always run this)
        logger.info("Using vision API directly as well")
        vision_items = parse_menu_image(image_data)
        logger.info(f"Vision API returned {len(vision_items)} items")
        
        # Step 3: Merge results, prioritizing vision results but using OCR for missing fields
        try:
            merged_items = merge_menu_items(vision_items, ocr_items)
            logger.info(f"Merged results: {len(merged_items)} items")
        except Exception as merge_error:
            logger.error(f"Error merging items: {str(merge_error)}")
            # Fall back to vision items only if merging fails
            merged_items = vision_items if vision_items else ocr_items
            logger.info(f"Falling back to {len(merged_items)} items from {'vision' if vision_items else 'OCR'}")
        
        if not merged_items:
            logger.error("Both extraction methods failed")
            return {"error": "Failed to extract menu items from image"}
        
        # Log extracted items
        logger.info("Final extracted menu items:")
        for i, item in enumerate(merged_items[:5]):
            if item:
                logger.info(f"  Item {i+1}: {item.get('name')} - {item.get('price')} - {item.get('category', 'No category')}")
        if len(merged_items) > 5:
            logger.info(f"  ... and {len(merged_items) - 5} more items")
        
        # Step 4: Map to schema
        menu_items = map_to_menu_items(restaurant_id, merged_items)
        logger.info(f"Mapped to {len(menu_items)} menu items")
        
        # Step 5: Verify data
        valid, error_msg = validate_menu_items(menu_items)
        if not valid:
            logger.error(f"Validation failed: {error_msg}")
            return {"error": error_msg}
        
        # Step 6: Send to API
        logger.info("Sending items to menu service API")
        success = send_menu_items(menu_items)
        if not success:
            return {"error": "Failed to create menu items"}
        
        return {
            "message": "Menu items processed successfully",
            "item_count": len(menu_items),
            "items": [
                {
                    "name": item.get("name"),
                    "price": item.get("price"),
                    "category": item.get("category", "(unknown category)")
                } 
                for item in merged_items[:10] if item
            ]  # Return first 10 items for preview
        }
        
    except Exception as e:
        logger.error(f"Error processing menu: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e)}

@router.get("/test-gemini")
async def test_gemini():
    """Test Gemini API connection."""
    try:
        from app.llm import model
        # Simple text prompt to test API
        response = model.generate_content("Hello, are you working? Say yes if you are.")
        return {"status": "success", "message": response.text}
    except Exception as e:
        logger.error(f"Gemini API test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}

@router.get("/check-models")
async def check_models():
    """Check available Gemini models."""
    try:
        import google.generativeai as genai
        models = genai.list_models()
        available_models = []
        for model in models:
            available_models.append({
                "name": model.name,
                "supported_methods": model.supported_generation_methods
            })
        return {"status": "success", "models": available_models}
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e)}