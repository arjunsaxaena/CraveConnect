from typing import List, Dict, Any, Tuple
from app.config import logger
from app.ocr import extract_text
from app.llm import parse_menu_text, parse_menu_image, merge_menu_items
from app.embedding import generate_menu_item_embedding
from app.schemas import map_to_menu_items, validate_menu_items
from app.api import send_menu_items_with_embeddings

class MenuProcessingPipeline:
    """Pipeline for processing menu images and extracting menu items."""
    
    def __init__(self):
        logger.info("Initializing MenuProcessingPipeline")
    
    def process(self, restaurant_id: str, menu_image_data: bytes) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Process menu image and extract menu items with embeddings.
        
        Returns:
            Tuple of (success, message, preview_items)
        """
        try:
            logger.info(f"Starting menu processing for restaurant: {restaurant_id}")
            
            # Step 1: OCR extraction
            logger.info("Step 1: OCR text extraction")
            ocr_text = extract_text(menu_image_data)
            if not ocr_text:
                logger.warning("OCR extraction returned empty text")
            else:
                logger.info(f"OCR extracted {len(ocr_text)} characters")
                
            # Try to parse the OCR text
            try:
                ocr_items = parse_menu_text(ocr_text) if ocr_text else []
                logger.info(f"OCR extracted {len(ocr_items)} items")
            except Exception as e:
                logger.error(f"Failed to parse OCR text: {str(e)}")
                ocr_items = []
            
            # Step 2: Vision extraction  
            logger.info("Step 2: Vision-based extraction")
            try:
                vision_items = parse_menu_image(menu_image_data)
                logger.info(f"Vision extracted {len(vision_items)} items")
            except Exception as e:
                logger.error(f"Failed in vision-based extraction: {str(e)}")
                vision_items = []
            
            # Step 3: Merge results
            logger.info("Step 3: Merging extraction results")
            merged_items = merge_menu_items(vision_items, ocr_items)
            
            if not merged_items:
                logger.error("Failed to extract any menu items from the image")
                return False, "Failed to extract menu items from image", []
            
            # Step 4: Map to menu service format
            logger.info("Step 4: Mapping to menu service format")
            menu_items = map_to_menu_items(restaurant_id, merged_items)
            
            if not menu_items:
                logger.error("No valid menu items could be mapped")
                return False, "No valid menu items could be extracted", []
            
            # Step 5: Validate menu items
            logger.info("Step 5: Validating menu items")
            valid, error_msg = validate_menu_items(menu_items)
            if not valid:
                logger.error(f"Validation failed: {error_msg}")
                return False, error_msg, []
            
            # Step 6: Generate embeddings
            logger.info("Step 6: Generating embeddings")
            embedding_success_count = 0
            for item in menu_items:
                embedding = generate_menu_item_embedding(item)
                if embedding:
                    item["embedding"] = embedding
                    embedding_success_count += 1
            
            logger.info(f"Generated embeddings for {embedding_success_count}/{len(menu_items)} items")
            
            # Step 7: Send to menu service
            logger.info("Step 7: Sending to menu service")
            success = send_menu_items_with_embeddings(menu_items)
            if not success:
                return False, "Failed to create menu items", []
            
            # Create preview (limit to 10 items)
            preview_items = [
                {
                    "name": item.get("name"),
                    "price": item.get("price"),
                    "description": item.get("description", "")[:50] + ("..." if len(item.get("description", "")) > 50 else ""),
                    "category": item.get("category", "(unknown category)"),
                    "has_embedding": "embedding" in item and item["embedding"] is not None
                } 
                for item in menu_items[:10]
            ]
            
            return True, f"Successfully processed {len(menu_items)} menu items", preview_items
            
        except Exception as e:
            logger.error(f"Error in menu processing pipeline: {str(e)}")
            return False, str(e), []