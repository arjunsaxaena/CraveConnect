from typing import List, Dict, Any, Optional, Tuple
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.schema import HumanMessage, SystemMessage
from backend.data_pipeline_service.app.config import logger
from backend.data_pipeline_service.app.ocr import extract_text
from backend.data_pipeline_service.app.llm import parse_menu_text, parse_menu_image, merge_menu_items
from backend.data_pipeline_service.app.embedding import generate_menu_item_embedding
from backend.data_pipeline_service.app.schemas import map_to_menu_items, validate_menu_items
from backend.data_pipeline_service.app.api import send_menu_items_with_embeddings

class MenuProcessingPipeline:
    """
    A complete pipeline for processing menu images.
    
    This pipeline:
    1. Extracts text from menu images using OCR
    2. Parses menu items from text using LLMs
    3. Parses menu items directly from images using LLMs
    4. Merges results from both approaches
    5. Generates embeddings for each menu item
    6. Sends menu items with embeddings to the menu service
    """
    
    def __init__(self):
        logger.info("Initializing MenuProcessingPipeline")
    
    def process(self, restaurant_id: str, menu_image_data: bytes) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Process a menu image and extract menu items with embeddings.
        
        Args:
            restaurant_id: ID of the restaurant
            menu_image_data: Binary image data
            
        Returns:
            Tuple containing:
            - success: Whether processing was successful
            - message: Status message
            - items: List of processed menu items (limited to 10 for response)
        """
        try:
            # Step 1: Extract text using OCR
            menu_text = extract_text(menu_image_data)
            ocr_items = []
            if menu_text and menu_text.strip():
                logger.info("Parsing menu text with LLM")
                ocr_items = parse_menu_text(menu_text)
            else:
                logger.warning("OCR text extraction failed or returned empty result")
            
            # Step 2: Use vision model to extract menu items directly from image
            logger.info("Parsing menu image with vision LLM")
            vision_items = parse_menu_image(menu_image_data)
            
            # Step 3: Merge results
            try:
                merged_items = merge_menu_items(vision_items, ocr_items)
            except Exception as merge_error:
                logger.error(f"Error merging items: {str(merge_error)}")
                merged_items = vision_items if vision_items else ocr_items
            
            if not merged_items:
                logger.error("Both extraction methods failed")
                return False, "Failed to extract menu items from image", []
            
            # Step 4: Map to menu service format
            menu_items = map_to_menu_items(restaurant_id, merged_items)
            
            # Step 5: Validate menu items
            valid, error_msg = validate_menu_items(menu_items)
            if not valid:
                logger.error(f"Validation failed: {error_msg}")
                return False, error_msg, []
            
            # Step 6: Generate embeddings for each menu item
            embedding_success_count = 0
            for item in menu_items:
                embedding = generate_menu_item_embedding(item)
                if embedding:
                    item["embedding"] = embedding
                    embedding_success_count += 1
            
            if embedding_success_count == 0 and len(menu_items) > 0:
                logger.warning(f"Failed to generate embeddings for all {len(menu_items)} menu items")
            else:
                logger.info(f"Generated embeddings for {embedding_success_count} out of {len(menu_items)} menu items")
            
            # Step 7: Send to menu service
            success = send_menu_items_with_embeddings(menu_items)
            if not success:
                return False, "Failed to create menu items", []
            
            # Return success and sample of items (limited to 10)
            preview_items = [
                {
                    "name": item.get("name"),
                    "price": item.get("price"),
                    "size": item.get("size", ""),
                    "category": item.get("category", "(unknown category)"),
                    "has_embedding": "embedding" in item and item["embedding"] is not None
                } 
                for item in menu_items[:10] if item
            ]
            
            return True, "Menu items processed successfully", preview_items
            
        except Exception as e:
            logger.error(f"Error in menu processing pipeline: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False, str(e), [] 