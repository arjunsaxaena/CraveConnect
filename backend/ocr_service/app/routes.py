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
    try:
        image_data = await menu_image.read()        

        menu_text = extract_text(image_data)
        ocr_items = []
        if menu_text and menu_text.strip():
            ocr_items = parse_menu_text(menu_text)
        else:
            logger.warning("OCR text extraction failed or returned empty result")
        
        vision_items = parse_menu_image(image_data)

        try:
            merged_items = merge_menu_items(vision_items, ocr_items)
        except Exception as merge_error:
            logger.error(f"Error merging items: {str(merge_error)}")
            merged_items = vision_items if vision_items else ocr_items
        
        if not merged_items:
            logger.error("Both extraction methods failed")
            return {"error": "Failed to extract menu items from image"}
        
        menu_items = map_to_menu_items(restaurant_id, merged_items)
        
        valid, error_msg = validate_menu_items(menu_items)
        if not valid:
            logger.error(f"Validation failed: {error_msg}")
            return {"error": error_msg}
        
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
            ]
        }
        
    except Exception as e:
        logger.error(f"Error processing menu: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e)}

# @router.get("/test-gemini")
# async def test_gemini():
#     """Test Gemini API connection."""
#     try:
#         from app.llm import model
#         # Simple text prompt to test API
#         response = model.generate_content("Hello, are you working? Say yes if you are.")
#         return {"status": "success", "message": response.text}
#     except Exception as e:
#         logger.error(f"Gemini API test failed: {e}")
#         import traceback
#         logger.error(traceback.format_exc())
#         return {"status": "error", "message": str(e)}

# @router.get("/check-models")
# async def check_models():
#     """Check available Gemini models."""
#     try:
#         import google.generativeai as genai
#         models = genai.list_models()
#         available_models = []
#         for model in models:
#             available_models.append({
#                 "name": model.name,
#                 "supported_methods": model.supported_generation_methods
#             })
#         return {"status": "success", "models": available_models}
#     except Exception as e:
#         logger.error(f"Failed to list models: {e}")
#         import traceback
#         logger.error(traceback.format_exc())
#         return {"status": "error", "message": str(e)}