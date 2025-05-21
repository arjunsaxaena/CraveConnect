"""
Menu Processor - Main module for the menu processing pipeline.

This module orchestrates the complete OCR and LLM processing pipeline:
1. Extract text via OCR
2. Structure the data via Gemini LLM
3. Map to database schema
4. Verify data quality
5. Send to API endpoint
"""
import os
import json
import logging
import dotenv
from typing import Dict, Any, Optional

# Import module components
from .ocr import ocr_image
from .llm import gemini_parse_menu
from .schema import map_to_menuitems
from .verification import verify_menu_items, verify_restaurant_exists
from .api import submit_menu_items_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()

def process_menu_image(
    image_path: str,
    restaurant_id: str,
    api_base_url: str,
    gemini_api_key: str,
    api_key: Optional[str] = None,
    image_base_path: Optional[str] = None,
    verify_only: bool = False,
    skip_restaurant_check: bool = False
) -> Dict[str, Any]:
    """
    Process a menu image through the complete pipeline.
    
    Pipeline:
    1. OCR text extraction
    2. LLM parsing to structured data
    3. Schema mapping
    4. Verification
    5. API submission (if verify_only=False)
    """
    try:
        # 1. Restaurant verification (if not skipped)
        if not skip_restaurant_check:
            if not verify_restaurant_exists(restaurant_id, api_base_url, api_key):
                return {
                    "success": False,
                    "error": f"Restaurant with ID {restaurant_id} not found"
                }
        
        # 2. OCR text extraction
        raw_text = ocr_image(image_path)
        
        # 3. LLM parsing
        parsed_items = gemini_parse_menu(raw_text, gemini_api_key)
        
        # 4. Schema mapping
        menu_items = map_to_menuitems(parsed_items, restaurant_id, image_base_path)
        
        # 5. Verification
        verification_result = verify_menu_items(menu_items)
        
        # Return early if verification failed or in verify-only mode
        if not verification_result["valid"] or verify_only:
            return {
                "success": verification_result["valid"],
                "verification": verification_result,
                "items_count": len(verification_result["items"])
            }
        
        # 6. API submission
        api_result = submit_menu_items_api(
            verification_result["items"],
            api_base_url,
            api_key
        )
        
        return {
            "success": True,
            "verification": verification_result,
            "api_response": api_result,
            "items_count": len(verification_result["items"])
        }
    
    except Exception as e:
        logger.error(f"Menu processing failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Example usage
    try:
        # Config from environment variables
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        API_BASE_URL = os.getenv("MENU_SERVICE_URL", "http://localhost:8002")
        API_KEY = os.getenv("API_KEY")
        
        # In a real application, these values would be fetched automatically:
        # - Restaurant ID would come from the authenticated user's context or API request
        # - Image path would come from file upload or a selected file in the UI
        
        # Example of how these might be fetched in a web application:
        # def process_uploaded_menu(request):
        #     restaurant_id = request.user.restaurant_id  # From authenticated user
        #     uploaded_file = request.FILES['menu_image']  # From form upload
        #     temp_image_path = save_temp_file(uploaded_file)
        
        RESTAURANT_ID = "sample-restaurant-uuid"  # In production: fetched from session/context
        SAMPLE_IMG = "../uploads/menu_images/sample_menu.jpg"  # In production: from file upload
        
        # First verify only to check extraction quality
        print("Verifying menu extraction...")
        result = process_menu_image(
            image_path=SAMPLE_IMG,
            restaurant_id=RESTAURANT_ID,
            api_base_url=API_BASE_URL,
            gemini_api_key=GEMINI_API_KEY,
            verify_only=True,
            skip_restaurant_check=True  # Skip for demo purposes
        )
        
        if result["success"]:
            print(f"Verification successful: {result['items_count']} items extracted")
            
            # Preview items (first 3)
            items = result["verification"]["items"][:3]
            for item in items:
                print(f"- {item['name']}: ${item['price']}")
            
            if len(result["verification"]["items"]) > 3:
                print(f"...and {len(result['verification']['items']) - 3} more items")
                
            # API submission confirmation
            if input("Submit to API? (y/n): ").lower() == 'y':
                submit_result = process_menu_image(
                    image_path=SAMPLE_IMG,
                    restaurant_id=RESTAURANT_ID,
                    api_base_url=API_BASE_URL,
                    gemini_api_key=GEMINI_API_KEY,
                    api_key=API_KEY
                )
                
                if submit_result["success"]:
                    print("API submission successful!")
                else:
                    print(f"API submission failed: {submit_result.get('error')}")
        else:
            print(f"Verification failed: {result.get('error', 'Unknown error')}")
            
            if "verification" in result:
                for item in result["verification"]["invalid_items"]:
                    print(f"- {item['item']['name']}: {', '.join(item['errors'])}")
    
    except Exception as e:
        print(f"Error: {e}")
