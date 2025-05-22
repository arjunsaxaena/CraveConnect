from fastapi import APIRouter, UploadFile, File, Form
from typing import Dict, Any
from app.config import logger
from app.ocr import extract_text
from app.llm import parse_menu_text, parse_menu_image, TEXT_MODEL
from app.schemas import map_to_menu_items, validate_menu_items
from app.api import send_menu_items

router = APIRouter()

@router.post("/process-menu")
async def process_menu(
    restaurant_id: str = Form(...),
    menu_image: UploadFile = File(...)
) -> Dict[str, Any]:
    """Process menu image and create menu items."""
    logger.info(f"Processing menu for restaurant_id: {restaurant_id}")
    
    try:
        # Step 1: Read image data
        image_data = await menu_image.read()
        logger.info(f"Read image data: {len(image_data)} bytes, content_type: {menu_image.content_type}")
        
        # Save image for debugging
        with open("debug_image.jpg", "wb") as f:
            f.write(image_data)
        logger.info("Saved debug image to disk")
        
        # Step 2: Extract text with OCR
        menu_text = extract_text(image_data)
        
        # Step 3: Parse with LLM
        items = []
        if menu_text.strip():
            logger.info("Sending text to LLM for parsing")
            items = parse_menu_text(menu_text)
            logger.info(f"LLM returned {len(items)} items")
        else:
            logger.warning("OCR text is empty, skipping text parsing")
            
        # Fallback to direct vision API if OCR+LLM didn't work
        if not items:
            logger.info("Text-based parsing failed, using vision API directly")
            items = parse_menu_image(image_data)
            logger.info(f"Vision API returned {len(items)} items")
        
        if not items:
            logger.error("Both text parsing and vision API failed to extract menu items")
            return {"error": "Failed to extract menu items from image"}
        
        # Log the extracted items
        logger.info("Extracted menu items:")
        for i, item in enumerate(items[:5]):  # Log first 5 items
            logger.info(f"  Item {i+1}: {item.get('name')} - Price: {item.get('price')}")
        if len(items) > 5:
            logger.info(f"  ... and {len(items) - 5} more items")
        
        # Step 4: Map to schema
        menu_items = map_to_menu_items(restaurant_id, items)
        
        # Step 5: Verify data
        valid, error_msg = validate_menu_items(menu_items)
        if not valid:
            logger.error(f"Validation failed: {error_msg}")
            return {"error": error_msg}
        
        # Step 6: Send to API
        logger.info("Sending items to menu service API")
        success = send_menu_items(menu_items)  # <-- Menu items already contain restaurant_id
        if not success:
            return {"error": "Failed to create menu items"}
        
        return {
            "message": "Menu items processed successfully",
            "item_count": len(menu_items),
            "items": items[:10]  # Return first 10 items for preview
        }
        
    except Exception as e:
        logger.error(f"Error processing menu: {str(e)}")
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