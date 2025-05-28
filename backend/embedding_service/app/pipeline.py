from typing import Tuple, List, Dict, Any
import time
from app.embedding import generate_menu_item_embedding
from app.ocr import ocr_tool
from app.menu_extractor import menu_extractor
from app.api import send_menu_items_with_embeddings
from app.config import logger

class MenuProcessingPipeline:
    """Pipeline for processing menu images and extracting menu items with embeddings."""
    
    async def process(self, restaurant_id: str, image_data: bytes) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Process menu image and extract menu items with embeddings."""
        try:
            # Extract text from image
            logger.info("Starting OCR text extraction...")
            start_time = time.time()
            menu_text = await self.extract_text(image_data)
            elapsed_time = time.time() - start_time
            
            if not menu_text:
                logger.warning("OCR extraction failed - no text extracted")
                return False, "Failed to extract text from menu image", []
                
            logger.info(f"OCR extraction complete in {elapsed_time:.2f}s. Text length: {len(menu_text)}")
                
            # Extract menu items using the universal extractor
            logger.info("Starting menu item extraction...")
            start_time = time.time()
            menu_items = await menu_extractor.extract_items(menu_text, restaurant_id)
            elapsed_time = time.time() - start_time
            
            if not menu_items:
                logger.warning("Menu item extraction failed - no items found")
                return False, "No menu items extracted from text", []
            
            logger.info(f"Menu item extraction complete in {elapsed_time:.2f}s. Items found: {len(menu_items)}")
                
            # Generate embeddings for menu items
            logger.info("Starting embedding generation...")
            start_time = time.time()
            items_with_embeddings = await self.add_embeddings(menu_items)
            elapsed_time = time.time() - start_time
            logger.info(f"Embedding generation complete in {elapsed_time:.2f}s")
            
            # Send items to database
            logger.info("Sending menu items to database...")
            start_time = time.time()
            success = await send_menu_items_with_embeddings(items_with_embeddings)
            elapsed_time = time.time() - start_time
            
            if not success:
                logger.warning("Failed to store some or all menu items in database")
                return True, "Menu processed but some items may not be stored", items_with_embeddings
                
            logger.info(f"Menu items stored in database in {elapsed_time:.2f}s")
            
            # Return results
            return True, "Successfully processed and stored menu", items_with_embeddings
            
        except Exception as e:
            logger.error(f"Error in menu processing pipeline: {str(e)}")
            return False, f"Error processing menu: {str(e)}", []

    async def extract_text(self, image_data: bytes) -> str:
        """Extract text from menu image."""
        if not ocr_tool:
            logger.warning("OCR tool not initialized")
            return ""
            
        try:
            return await ocr_tool.arun(image_data)
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            return ""

    async def add_embeddings(self, menu_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embeddings to menu items."""
        if not menu_items:
            return []
            
        result = []
        
        for item in menu_items:
            try:
                embedding = await generate_menu_item_embedding(item)
                
                if embedding:
                    item["embedding"] = embedding
                    
                result.append(item)
                
            except Exception as e:
                logger.error(f"Error adding embedding to menu item: {str(e)}")
                # Still add the item without embedding
                result.append(item)
                
        return result