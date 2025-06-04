from typing import Tuple, List, Dict, Any
import time
import aiohttp
from app.embedding import generate_menu_item_embedding, generate_embedding
from app.ocr import ocr_tool, OCRTool
from app.menu_extractor import menu_extractor, MenuItemExtractor
from app.config import logger, MENU_SERVICE_URL

class MenuProcessingPipeline:
    def __init__(self):
        self.extractor = menu_extractor
    
    async def process(self, restaurant_id: str, image_data: bytes) -> Tuple[bool, str, List[Dict[str, Any]]]:
        try:
            if not ocr_tool:
                logger.error("OCR tool not initialized")
                return False, "OCR tool not initialized", []
                
            # Extract text from image using OCR
            text = await ocr_tool.arun(image_data)
            if not text:
                return False, "Failed to extract text from image", []
            
            logger.info(f"Extracted text from image: {text[:100]}...")
            
            # Extract menu items and categories using LLM
            menu_items = await self.extractor.extract_and_create(text, restaurant_id)
            if not menu_items:
                return False, "Failed to extract menu items", []
            
            logger.info(f"Extracted {len(menu_items)} menu items")
            
            # Add embeddings to menu items
            items_with_embeddings = []
            for item in menu_items:
                text_for_embedding = f"{item['name']}"
                if item.get("description"):
                    text_for_embedding += f" {item['description']}"
                
                embedding = await generate_embedding(text_for_embedding)
                item["embedding"] = embedding
                items_with_embeddings.append(item)
            
            try:
                logger.info(f"Sending {len(items_with_embeddings)} menu items to database at {MENU_SERVICE_URL}/api/menu")
                async with aiohttp.ClientSession() as client:
                    async with client.post(f"{MENU_SERVICE_URL}/api/menu", 
                                         json={"restaurant_id": restaurant_id, "menu_items": items_with_embeddings}) as response:
                        if response.status not in [200, 201]:
                            error_text = await response.text()
                            logger.error(f"Failed to create menu items: {response.status}, {error_text}")
                            return False, f"Failed to create menu items: {error_text}", items_with_embeddings
                        
                        logger.info(f"Successfully sent {len(items_with_embeddings)} menu items to menu service")
            except Exception as e:
                logger.error(f"Failed to send menu items to menu service: {str(e)}")
                return False, f"Failed to save menu items: {str(e)}", items_with_embeddings
            
            return True, f"Successfully processed {len(items_with_embeddings)} items", items_with_embeddings
            
        except Exception as e:
            logger.error(f"Error in pipeline processing: {str(e)}")
            return False, str(e), []

    async def extract_text(self, image_data: bytes) -> str:
        if not ocr_tool:
            logger.warning("OCR tool not initialized")
            return ""
            
        try:
            return await ocr_tool.arun(image_data)
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            return ""

    async def add_embeddings(self, menu_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
                result.append(item)
                
        return result

    async def send_menu_items_to_database(self, restaurant_id, menu_items):
        import aiohttp
        from app.config import MENU_SERVICE_URL, logger
        
        logger.info(f"Sending {len(menu_items)} menu items to database at {MENU_SERVICE_URL}/menu")
        
        async with aiohttp.ClientSession() as client:
            async with client.post(f"{MENU_SERVICE_URL}/menu", json={"restaurant_id": restaurant_id, "menu_items": menu_items}) as response:
                result = await response.json()
                
        logger.info(f"Sent {len(menu_items)}/{len(menu_items)} menu items (100%)")
        return result